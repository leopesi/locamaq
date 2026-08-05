from django.contrib import admin
from .models import Equipment, EquipmentHistory


class EquipmentHistoryInline(admin.TabularInline):
    model = EquipmentHistory
    extra = 0
    readonly_fields = ['previous_state', 'new_state', 'changed_by', 'created_at']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'state', 'daily_rate', 'tenant']
    list_filter = ['state', 'category', 'tenant']
    search_fields = ['code', 'name']
    inlines = [EquipmentHistoryInline]
