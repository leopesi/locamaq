from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'value', 'description', 'rental', 'tenant']
    list_filter = ['type', 'tenant', 'date']
    search_fields = ['description']
