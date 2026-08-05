from django.db import models


class Customer(models.Model):
    """Customer of a tenant — complete data for rental management."""

    class PersonType(models.TextChoices):
        INDIVIDUAL = 'pf', 'Pessoa Física'
        COMPANY = 'pj', 'Pessoa Jurídica'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='customers',
    )

    # Tipo e identificação
    person_type = models.CharField(
        'Tipo',
        max_length=2,
        choices=PersonType.choices,
        default=PersonType.INDIVIDUAL,
    )
    name = models.CharField('Nome / Razão Social', max_length=200)
    trade_name = models.CharField('Nome Fantasia', max_length=200, blank=True)
    document = models.CharField('CPF/CNPJ', max_length=18, blank=True)
    rg = models.CharField('RG / Inscrição Estadual', max_length=30, blank=True)

    # Contato principal
    phone = models.CharField('Telefone', max_length=20, blank=True)
    phone2 = models.CharField('Telefone 2', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)

    # Endereço completo
    zip_code = models.CharField('CEP', max_length=10, blank=True)
    address = models.CharField('Endereço', max_length=300, blank=True)
    number = models.CharField('Número', max_length=20, blank=True)
    complement = models.CharField('Complemento', max_length=100, blank=True)
    neighborhood = models.CharField('Bairro', max_length=100, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('UF', max_length=2, blank=True)

    # Endereço de entrega (obra)
    delivery_address = models.CharField('Endereço de Entrega/Obra', max_length=300, blank=True)
    delivery_number = models.CharField('Número (entrega)', max_length=20, blank=True)
    delivery_neighborhood = models.CharField('Bairro (entrega)', max_length=100, blank=True)
    delivery_city = models.CharField('Cidade (entrega)', max_length=100, blank=True)
    delivery_state = models.CharField('UF (entrega)', max_length=2, blank=True)
    delivery_reference = models.CharField('Referência/Ponto de Referência', max_length=200, blank=True)

    # Contato na obra
    site_contact_name = models.CharField('Responsável na Obra', max_length=200, blank=True)
    site_contact_phone = models.CharField('Telefone do Responsável', max_length=20, blank=True)

    # Referências e garantias
    reference1_name = models.CharField('Referência 1 - Nome', max_length=200, blank=True)
    reference1_phone = models.CharField('Referência 1 - Telefone', max_length=20, blank=True)
    reference2_name = models.CharField('Referência 2 - Nome', max_length=200, blank=True)
    reference2_phone = models.CharField('Referência 2 - Telefone', max_length=20, blank=True)

    # Financeiro
    credit_limit = models.DecimalField('Limite de Crédito', max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField('Condição de Pagamento', max_length=100, blank=True,
        help_text='Ex: À vista, 30 dias, 7/14/21 dias')

    # Observações e controle
    notes = models.TextField('Observações', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    is_blocked = models.BooleanField('Bloqueado', default=False,
        help_text='Cliente com pendências ou inadimplente')
    block_reason = models.CharField('Motivo do Bloqueio', max_length=200, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']
        unique_together = ['tenant', 'document']

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        parts = [self.address, self.number, self.complement, self.neighborhood, self.city, self.state]
        return ', '.join(p for p in parts if p)

    @property
    def full_delivery_address(self):
        parts = [self.delivery_address, self.delivery_number, self.delivery_neighborhood, self.delivery_city, self.delivery_state]
        return ', '.join(p for p in parts if p)
