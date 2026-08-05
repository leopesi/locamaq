from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator that restricts access to admin users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, 'Acesso restrito a administradores.')
            return redirect('tenants:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def tenant_required(view_func):
    """Decorator that ensures user has a tenant assigned."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.tenant:
            messages.error(request, 'Nenhuma empresa vinculada ao seu usuário.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper
