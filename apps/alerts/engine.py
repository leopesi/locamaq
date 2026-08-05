"""
Alert engine — checks conditions and creates notifications.
"""
import logging
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.alerts.models import AlertRule, Notification
from apps.rentals.models import Rental
from apps.inventory.models import Equipment
from apps.finance.models import Transaction
from apps.notifications.services import EvolutionAPIService

logger = logging.getLogger('locamaq')


class AlertEngine:
    """Evaluates alert rules and creates notifications."""

    def __init__(self, tenant):
        self.tenant = tenant
        self.today = date.today()

    def run_all_checks(self):
        """Run all active alert checks for this tenant."""
        rules = AlertRule.objects.filter(tenant=self.tenant, is_active=True)
        results = []

        for rule in rules:
            checker = getattr(self, f'_check_{rule.alert_type}', None)
            if checker:
                notifications = checker(rule)
                results.extend(notifications)

        return results

    def _check_overdue_rental(self, rule):
        """Check for overdue rentals (devolução atrasada)."""
        threshold_days = rule.threshold or 1
        overdue_rentals = Rental.objects.filter(
            tenant=self.tenant,
            status='active',
            expected_return__lt=self.today,
        )

        notifications = []
        for rental in overdue_rentals:
            days_overdue = (self.today - rental.expected_return).days
            if days_overdue >= threshold_days:
                # Avoid duplicates (check last 24h)
                exists = Notification.objects.filter(
                    tenant=self.tenant,
                    alert_type='overdue_rental',
                    related_rental=rental,
                    created_at__date=self.today,
                ).exists()

                if not exists:
                    notif = self._create_notification(
                        rule=rule,
                        title=f'⏰ Devolução atrasada: Locação #{rental.pk} ({days_overdue} dia{"s" if days_overdue > 1 else ""})',
                        message=f'Cliente: {rental.customer.name}\n'
                                f'Telefone: {rental.customer.phone}\n'
                                f'Devolução prevista: {rental.expected_return.strftime("%d/%m/%Y")}\n'
                                f'Dias de atraso: {days_overdue}\n'
                                f'Valor: R$ {rental.total_value}\n'
                                f'Endereço: {rental.delivery_address}',
                        related_rental=rental,
                        related_customer=rental.customer,
                    )
                    notifications.append(notif)

        return notifications

    def _check_low_available(self, rule):
        """Check if available equipment count is below threshold."""
        threshold = rule.threshold or 3
        available_count = Equipment.objects.filter(
            tenant=self.tenant, state='available'
        ).count()

        if available_count <= threshold:
            exists = Notification.objects.filter(
                tenant=self.tenant,
                alert_type='low_available',
                created_at__date=self.today,
            ).exists()

            if not exists:
                total = Equipment.objects.filter(tenant=self.tenant).count()
                notif = self._create_notification(
                    rule=rule,
                    title=f'Apenas {available_count} equipamento(s) disponível(is)',
                    message=f'Total de equipamentos: {total}\n'
                            f'Disponíveis: {available_count}\n'
                            f'Limite configurado: {threshold}',
                )
                return [notif]

        return []

    def _check_payment_overdue(self, rule):
        """Check for unpaid rentals and overdue transactions."""
        threshold_days = rule.threshold or 7

        # Marcar transações pendentes como atrasadas se due_date passou
        from apps.finance.models import Transaction
        overdue_transactions = Transaction.objects.filter(
            tenant=self.tenant,
            payment_status='pending',
            due_date__lt=self.today,
        )
        for tx in overdue_transactions:
            tx.payment_status = 'overdue'
            tx.save()

        # Gerar notificações para locações com pagamento atrasado
        unpaid_rentals = Rental.objects.filter(
            tenant=self.tenant,
            status='active',
            is_paid=False,
            start_date__lte=self.today,
        )

        notifications = []
        for rental in unpaid_rentals:
            days_active = (self.today - rental.start_date).days
            if days_active >= threshold_days:
                exists = Notification.objects.filter(
                    tenant=self.tenant,
                    alert_type='payment_overdue',
                    related_rental=rental,
                    created_at__date=self.today,
                ).exists()

                if not exists:
                    notif = self._create_notification(
                        rule=rule,
                        title=f'💸 Pagamento atrasado: Locação #{rental.pk}',
                        message=f'Cliente: {rental.customer.name}\n'
                                f'Valor: R$ {rental.total_value}\n'
                                f'Forma: {rental.get_payment_method_display()}\n'
                                f'Dias sem pagamento: {days_active}',
                        related_rental=rental,
                        related_customer=rental.customer,
                    )
                    notifications.append(notif)

        return notifications

    def _check_equipment_maintenance(self, rule):
        """Check equipment in maintenance for too long."""
        from apps.inventory.models import EquipmentHistory
        threshold_days = rule.threshold or 15

        maintenance_eq = Equipment.objects.filter(
            tenant=self.tenant, state='maintenance'
        )

        notifications = []
        for eq in maintenance_eq:
            # Find when it entered maintenance
            last_change = eq.history.filter(new_state='maintenance').first()
            if last_change:
                days_in_maintenance = (timezone.now() - last_change.created_at).days
                if days_in_maintenance >= threshold_days:
                    exists = Notification.objects.filter(
                        tenant=self.tenant,
                        alert_type='equipment_maintenance',
                        related_equipment=eq,
                        created_at__date=self.today,
                    ).exists()

                    if not exists:
                        notif = self._create_notification(
                            rule=rule,
                            title=f'Equipamento {eq.code} em manutenção há {days_in_maintenance} dias',
                            message=f'Equipamento: {eq.name}\n'
                                    f'Código: {eq.code}\n'
                                    f'Em manutenção desde: {last_change.created_at.strftime("%d/%m/%Y")}',
                            related_equipment=eq,
                        )
                        notifications.append(notif)

        return notifications

    def _check_high_expense(self, rule):
        """Check if monthly expenses exceed threshold."""
        threshold_value = Decimal(str(rule.threshold or 5000))
        month_start = self.today.replace(day=1)

        monthly_expense = Transaction.objects.filter(
            tenant=self.tenant,
            type='expense',
            date__gte=month_start,
            date__lte=self.today,
        ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        if monthly_expense >= threshold_value:
            exists = Notification.objects.filter(
                tenant=self.tenant,
                alert_type='high_expense',
                created_at__date=self.today,
            ).exists()

            if not exists:
                notif = self._create_notification(
                    rule=rule,
                    title=f'Despesas do mês: R$ {monthly_expense}',
                    message=f'Total de despesas no mês: R$ {monthly_expense}\n'
                            f'Limite configurado: R$ {threshold_value}',
                )
                return [notif]

        return []

    def _create_notification(self, rule, title, message, **kwargs):
        """Create a notification and optionally send via WhatsApp."""
        notif = Notification.objects.create(
            tenant=self.tenant,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title,
            message=message,
            related_rental=kwargs.get('related_rental'),
            related_equipment=kwargs.get('related_equipment'),
            related_customer=kwargs.get('related_customer'),
        )

        # Send WhatsApp if configured
        if rule.notify_channel in ['whatsapp', 'both'] and rule.notify_phone:
            try:
                service = EvolutionAPIService.from_tenant(self.tenant)
                whatsapp_msg = f'{notif.severity_icon} *{title}*\n\n{message}'
                service.send_text(rule.notify_phone, whatsapp_msg)
                notif.whatsapp_sent = True
                notif.save()
            except Exception as e:
                logger.error(f'Failed to send alert WhatsApp: {e}')

        logger.info(f'Alert created: [{rule.severity}] {title} | Tenant: {self.tenant.name}')
        return notif
