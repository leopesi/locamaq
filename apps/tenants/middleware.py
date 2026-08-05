from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages


class TenantMiddleware(MiddlewareMixin):
    """
    Multi-tenant middleware.
    - Injects tenant into request based on logged-in user
    - Blocks access if user has no tenant assigned
    - Ensures complete data isolation between tenants
    """

    EXEMPT_URLS = ['/accounts/login/', '/accounts/logout/', '/admin/']

    def process_request(self, request):
        request.tenant = None

        if request.user.is_authenticated:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                request.tenant = request.user.tenant
            else:
                # User without tenant — block unless exempt URL or superuser in admin
                path = request.path
                if not any(path.startswith(url) for url in self.EXEMPT_URLS):
                    if not request.user.is_superuser:
                        messages.error(request, 'Seu usuário não está vinculado a nenhuma empresa. Contate o administrador.')
                        from django.contrib.auth import logout
                        logout(request)
                        return redirect('accounts:login')
