from django.contrib import admin
from .models import Rental, RentalItem


class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'period_type', 'start_date', 'expected_return', 'status', 'total_value']
    list_filter = ['status', 'period_type', 'tenant']
    search_fields = ['customer__name']
    inlines = [RentalItemInline]
