"""
Multi-tenant mixins and utilities.
Ensure data isolation between tenants.
"""

from django.db import models


class TenantQuerySet(models.QuerySet):
    """QuerySet that automatically filters by tenant."""

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    """Manager that provides tenant-aware querysets."""

    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
