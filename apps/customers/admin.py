from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'person_type', 'document', 'phone', 'whatsapp', 'city', 'is_blocked', 'tenant']
    list_filter = ['person_type', 'tenant', 'is_active', 'is_blocked', 'city', 'state']
    search_fields = ['name', 'trade_name', 'document', 'phone', 'whatsapp']
    fieldsets = (
        ('Identificação', {'fields': ('tenant', 'person_type', 'name', 'trade_name', 'document', 'rg')}),
        ('Contato', {'fields': ('phone', 'phone2', 'whatsapp', 'email')}),
        ('Endereço', {'fields': ('zip_code', 'address', 'number', 'complement', 'neighborhood', 'city', 'state')}),
        ('Entrega/Obra', {'fields': ('delivery_address', 'delivery_number', 'delivery_neighborhood', 'delivery_city', 'delivery_state', 'delivery_reference', 'site_contact_name', 'site_contact_phone')}),
        ('Referências', {'fields': ('reference1_name', 'reference1_phone', 'reference2_name', 'reference2_phone')}),
        ('Financeiro', {'fields': ('credit_limit', 'payment_terms')}),
        ('Controle', {'fields': ('notes', 'is_active', 'is_blocked', 'block_reason')}),
    )
