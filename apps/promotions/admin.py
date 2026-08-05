from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'tenant', 'sent_at', 'recipients_count', 'created_by']
    list_filter = ['tenant']
    search_fields = ['title', 'message']
