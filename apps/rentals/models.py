from django.db import models
from decimal import Decimal


class Rental(models.Model):
    """A rental contract."""

    class PeriodType(models.TextChoices):
        DAILY = 'daily', 'Diária'
        WEEKLY = 'weekly', 'Semanal'
        MONTHLY = 'monthly', 'Mensal'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        RETURNED = 'returned', 'Devolvida'
        OVERDUE = 'overdue', 'Atrasada'
        CANCELLED = 'cancelled', 'Cancelada'

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'À Vista (Dinheiro)'
        PIX = 'pix', 'PIX'
        CREDIT_CARD = 'credit_card', 'Cartão de Crédito'
        DEBIT_CARD = 'debit_card', 'Cartão de Débito'
        LATER = 'later', 'A Receber (Depois)'
        TRANSFER = 'transfer', 'Transferência Bancária'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='rentals',
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='rentals',
        verbose_name='Cliente',
    )
    period_type = models.CharField(
        'Tipo de Período',
        max_length=10,
        choices=PeriodType.choices,
        default=PeriodType.DAILY,
    )
    start_date = models.DateField('Data de Início')
    expected_return = models.DateField('Devolução Prevista')
    actual_return = models.DateField('Devolução Real', null=True, blank=True)
    status = models.CharField(
        'Status',
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    total_value = models.DecimalField('Valor Total', max_digits=12, decimal_places=2, default=0)

    # Pagamento
    payment_method = models.CharField(
        'Forma de Pagamento',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.LATER,
    )
    is_paid = models.BooleanField('Pago', default=False)
    paid_at = models.DateField('Data do Pagamento', null=True, blank=True)

    # Endereço de entrega
    delivery_address = models.CharField('Endereço de Entrega', max_length=300, blank=True)
    delivery_reference = models.CharField('Ponto de Referência', max_length=200, blank=True)
    delivery_contact = models.CharField('Responsável no Local', max_length=200, blank=True)
    delivery_phone = models.CharField('Telefone do Responsável', max_length=20, blank=True)
    delivery_lat = models.DecimalField('Latitude', max_digits=10, decimal_places=7, null=True, blank=True)
    delivery_lng = models.DecimalField('Longitude', max_digits=10, decimal_places=7, null=True, blank=True)
    delivery_distance_km = models.DecimalField('Distância (km)', max_digits=6, decimal_places=1, null=True, blank=True)
    delivery_time_min = models.IntegerField('Tempo estimado (min)', null=True, blank=True)

    notes = models.TextField('Observações', blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Criado por',
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Locação'
        verbose_name_plural = 'Locações'
        ordering = ['-created_at']

    def __str__(self):
        return f'Locação #{self.pk} - {self.customer.name}'

    def calculate_total(self):
        """Recalculates total based on rental items."""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.calculate_value()
        self.total_value = total
        return total


class RentalItem(models.Model):
    """An equipment included in a rental."""

    rental = models.ForeignKey(
        Rental,
        on_delete=models.CASCADE,
        related_name='items',
    )
    equipment = models.ForeignKey(
        'inventory.Equipment',
        on_delete=models.PROTECT,
        related_name='rental_items',
        verbose_name='Equipamento',
    )
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    unit_value = models.DecimalField('Valor Unitário', max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item da Locação'
        verbose_name_plural = 'Itens da Locação'

    def __str__(self):
        return f'{self.equipment.name} - {self.rental}'

    def calculate_value(self):
        """Calculate value based on rental period type."""
        return self.unit_value * self.quantity
