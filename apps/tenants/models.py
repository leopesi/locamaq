from django.db import models


class Tenant(models.Model):
    """Represents a company/organization using the platform."""

    name = models.CharField('Nome da Empresa', max_length=200)
    document = models.CharField('CNPJ', max_length=18, unique=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    address = models.TextField('Endereço', blank=True)
    logo = models.ImageField('Logo', upload_to='tenants/logos/', blank=True, null=True)

    # Cláusulas do contrato de locação
    contract_clauses = models.TextField('Cláusulas do Contrato', blank=True)
    return_conditions = models.TextField('Condições de Devolução', blank=True)
    penalty_terms = models.TextField('Termos de Multa', blank=True)

    # Evolution API config per tenant
    evolution_api_url = models.CharField('Evolution API URL', max_length=300, blank=True,
        help_text='Ex: http://localhost:8080 ou https://evolution.seudominio.com')
    evolution_api_key = models.CharField('Evolution API Key', max_length=200, blank=True)
    evolution_instance = models.CharField('Instância Evolution', max_length=100, blank=True)

    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['name']

    def __str__(self):
        return self.name
