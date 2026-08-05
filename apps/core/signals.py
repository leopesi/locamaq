"""
LocaMaq — Signals for cache invalidation.
Automatically clears cache when relevant data changes.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.core.cache import invalidate_tenant_cache
from apps.rentals.models import Rental, RentalItem
from apps.inventory.models import Equipment
from apps.finance.models import Transaction


@receiver([post_save, post_delete], sender=Rental)
def invalidate_on_rental_change(sender, instance, **kwargs):
    """Invalidate dashboard cache when a rental changes."""
    if instance.tenant_id:
        invalidate_tenant_cache(instance.tenant_id)


@receiver([post_save, post_delete], sender=RentalItem)
def invalidate_on_rental_item_change(sender, instance, **kwargs):
    """Invalidate cache when rental items change."""
    if instance.rental and instance.rental.tenant_id:
        invalidate_tenant_cache(instance.rental.tenant_id)


@receiver([post_save, post_delete], sender=Equipment)
def invalidate_on_equipment_change(sender, instance, **kwargs):
    """Invalidate cache when equipment changes."""
    if instance.tenant_id:
        invalidate_tenant_cache(instance.tenant_id)


@receiver([post_save, post_delete], sender=Transaction)
def invalidate_on_transaction_change(sender, instance, **kwargs):
    """Invalidate cache when transactions change."""
    if instance.tenant_id:
        invalidate_tenant_cache(instance.tenant_id)
