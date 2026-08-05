"""
LocaMaq — Cache utilities.
Tenant-aware caching with explicit invalidation.
"""

import hashlib
from functools import wraps

from django.core.cache import cache


def tenant_cache_key(tenant_id, prefix, *args):
    """Generate a cache key scoped to a tenant."""
    parts = f'{prefix}:tenant_{tenant_id}:' + ':'.join(str(a) for a in args)
    return hashlib.md5(parts.encode()).hexdigest()


def invalidate_tenant_cache(tenant_id, prefix=None):
    """Invalidate cache for a tenant."""
    if prefix:
        key = tenant_cache_key(tenant_id, prefix)
        cache.delete(key)
    else:
        for p in ['dashboard_stats', 'equipment_stats', 'finance_summary', 'map_data']:
            key = tenant_cache_key(tenant_id, p)
            cache.delete(key)


def get_or_set_tenant_cache(tenant_id, prefix, callback, timeout=300, *args):
    """Get from cache or compute and store."""
    key = tenant_cache_key(tenant_id, prefix, *args)
    result = cache.get(key)
    if result is None:
        result = callback()
        cache.set(key, result, timeout)
    return result


def invalidate_on_write(view_func):
    """Decorator that invalidates tenant cache after a successful POST."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if request.method == 'POST' and request.tenant:
            if hasattr(response, 'status_code') and response.status_code in (301, 302):
                invalidate_tenant_cache(request.tenant.pk)
        return response
    return wrapper
