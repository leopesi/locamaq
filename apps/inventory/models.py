from django.db import models


class Equipment(models.Model):
    """Individual equipment tracked by patrimony code."""

    class State(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        RENTED = 'rented', 'Locado'
        MAINTENANCE = 'maintenance', 'Em Manutenção'
        RETIRED = 'retired', 'Baixado'

    class Category(models.TextChoices):
        SCAFFOLDING = 'scaffolding', 'Andaime'
        MIXER = 'mixer', 'Betoneira'
        COMPACTOR = 'compactor', 'Compactador'
        GENERATOR = 'generator', 'Gerador'
        PUMP = 'pump', 'Bomba'
        OTHER = 'other', 'Outros'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='equipments',
    )
    code = models.CharField('Código Patrimônio', max_length=50)
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True)
    category = models.CharField(
        'Categoria',
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )
    state = models.CharField(
        'Estado',
        max_length=20,
        choices=State.choices,
        default=State.AVAILABLE,
    )
    daily_rate = models.DecimalField('Valor Diária', max_digits=10, decimal_places=2, default=0)
    weekly_rate = models.DecimalField('Valor Semanal', max_digits=10, decimal_places=2, default=0)
    monthly_rate = models.DecimalField('Valor Mensal', max_digits=10, decimal_places=2, default=0)
    image = models.ImageField('Imagem', upload_to='equipments/', blank=True, null=True)
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['code']
        unique_together = ['tenant', 'code']

    def __str__(self):
        return f'[{self.code}] {self.name}'

    @property
    def is_available(self):
        return self.state == self.State.AVAILABLE


class EquipmentHistory(models.Model):
    """Log of equipment state changes."""

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='history',
    )
    previous_state = models.CharField('Estado Anterior', max_length=20, choices=Equipment.State.choices)
    new_state = models.CharField('Novo Estado', max_length=20, choices=Equipment.State.choices)
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico do Equipamento'
        verbose_name_plural = 'Histórico dos Equipamentos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.equipment.code}: {self.previous_state} → {self.new_state}'
