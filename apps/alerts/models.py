from django.db import models


class AlertRule(models.Model):
    """Configuration rules for automatic alerts."""

    class AlertType(models.TextChoices):
        OVERDUE_RENTAL = 'overdue_rental', 'Locação Atrasada'
        EQUIPMENT_MAINTENANCE = 'equipment_maintenance', 'Equipamento em Manutenção há muito tempo'
        LOW_AVAILABLE = 'low_available', 'Poucos Equipamentos Disponíveis'
        PAYMENT_OVERDUE = 'payment_overdue', 'Pagamento Pendente'
        HIGH_EXPENSE = 'high_expense', 'Despesa Alta no Mês'
        CUSTOMER_BLOCKED = 'customer_blocked', 'Cliente Bloqueado Tentou Locar'
        SYSTEM_ERROR = 'system_error', 'Erro Crítico no Sistema'
        WHATSAPP_DOWN = 'whatsapp_down', 'WhatsApp Desconectado'

    class Severity(models.TextChoices):
        CRITICAL = 'critical', 'Crítico'
        WARNING = 'warning', 'Alerta'
        INFO = 'info', 'Informativo'

    class NotifyChannel(models.TextChoices):
        SYSTEM = 'system', 'Apenas no Sistema'
        WHATSAPP = 'whatsapp', 'WhatsApp do Admin'
        BOTH = 'both', 'Sistema + WhatsApp'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='alert_rules',
    )
    alert_type = models.CharField('Tipo de Alerta', max_length=30, choices=AlertType.choices)
    severity = models.CharField('Severidade', max_length=10, choices=Severity.choices, default=Severity.WARNING)
    is_active = models.BooleanField('Ativo', default=True)
    notify_channel = models.CharField(
        'Canal de Notificação', max_length=10,
        choices=NotifyChannel.choices, default=NotifyChannel.SYSTEM
    )
    threshold = models.IntegerField(
        'Limite/Threshold', default=0,
        help_text='Ex: dias de atraso, qtd mínima disponível, valor máximo'
    )
    notify_phone = models.CharField('WhatsApp para Notificar', max_length=20, blank=True,
        help_text='Número do admin para receber alertas críticos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Regra de Alerta'
        verbose_name_plural = 'Regras de Alerta'
        unique_together = ['tenant', 'alert_type']
        ordering = ['alert_type']

    def __str__(self):
        return f'{self.get_alert_type_display()} ({self.get_severity_display()})'


class Notification(models.Model):
    """System notifications for admins/operators."""

    class Status(models.TextChoices):
        UNREAD = 'unread', 'Não Lida'
        READ = 'read', 'Lida'
        DISMISSED = 'dismissed', 'Dispensada'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    alert_type = models.CharField('Tipo', max_length=30, choices=AlertRule.AlertType.choices)
    severity = models.CharField('Severidade', max_length=10, choices=AlertRule.Severity.choices)
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensagem')
    status = models.CharField('Status', max_length=10, choices=Status.choices, default=Status.UNREAD)

    # Referência opcional
    related_rental = models.ForeignKey(
        'rentals.Rental', on_delete=models.SET_NULL, null=True, blank=True
    )
    related_equipment = models.ForeignKey(
        'inventory.Equipment', on_delete=models.SET_NULL, null=True, blank=True
    )
    related_customer = models.ForeignKey(
        'customers.Customer', on_delete=models.SET_NULL, null=True, blank=True
    )

    # Para qual usuário (null = todos admins do tenant)
    target_user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True
    )

    whatsapp_sent = models.BooleanField('WhatsApp Enviado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    read_at = models.DateTimeField('Lido em', null=True, blank=True)

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_severity_display()}] {self.title}'

    @property
    def severity_icon(self):
        icons = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🔵',
        }
        return icons.get(self.severity, '⚪')
