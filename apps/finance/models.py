from django.db import models


class Transaction(models.Model):
    """Financial transaction (income or expense)."""

    class Type(models.TextChoices):
        INCOME = 'income', 'Entrada'
        EXPENSE = 'expense', 'Saída'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    type = models.CharField('Tipo', max_length=10, choices=Type.choices)
    value = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    description = models.CharField('Descrição', max_length=300)
    date = models.DateField('Data')
    rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='Locação Relacionada',
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-date', '-created_at']

    def __str__(self):
        signal = '+' if self.type == self.Type.INCOME else '-'
        return f'{signal} R$ {self.value} - {self.description}'
