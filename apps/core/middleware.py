"""
LocaMaq — Error handling middleware.
Catches unhandled exceptions and logs them properly.
"""

import logging
import traceback

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger('locamaq')
security_logger = logging.getLogger('locamaq.security')


class ErrorHandlingMiddleware:
    """
    Global error handling middleware.
    - Catches unhandled exceptions
    - Logs with full traceback
    - Shows friendly error page in production
    - Logs 403/404 for security monitoring
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log 403 (Forbidden) for security
        if response.status_code == 403:
            security_logger.warning(
                f'403 Forbidden: {request.path} | User: {request.user} | IP: {self._get_ip(request)}'
            )

        # Log 404 (Not Found) — possible probing
        if response.status_code == 404:
            logger.info(f'404 Not Found: {request.path} | IP: {self._get_ip(request)}')

        return response

    def process_exception(self, request, exception):
        """Handle uncaught exceptions."""
        # Get request context
        user = getattr(request, 'user', None)
        tenant = getattr(request, 'tenant', None)
        ip = self._get_ip(request)

        # Log the error
        logger.error(
            f'Unhandled Exception: {type(exception).__name__}: {str(exception)} | '
            f'Path: {request.path} | Method: {request.method} | '
            f'User: {user} | Tenant: {tenant} | IP: {ip}\n'
            f'{traceback.format_exc()}'
        )

        # In production, show friendly error page
        if not settings.DEBUG:
            return render(request, 'errors/500.html', status=500)

        # In debug mode, let Django show the default error page
        return None

    def _get_ip(self, request):
        """Get client IP from request."""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class AuditMiddleware:
    """
    Audit middleware — logs important write operations.
    """

    AUDIT_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    def __init__(self, get_response):
        self.get_response = get_response
        self.audit_logger = logging.getLogger('locamaq.audit')

    def __call__(self, request):
        response = self.get_response(request)

        # Only audit write operations that succeeded (2xx or 3xx redirect)
        if (request.method in self.AUDIT_METHODS and
                response.status_code in range(200, 400) and
                not request.path.startswith('/admin/')):

            user = getattr(request, 'user', None)
            tenant = getattr(request, 'tenant', None)

            self.audit_logger.info(
                f'{request.method} {request.path} → {response.status_code} | '
                f'User: {user} | Tenant: {tenant}'
            )

        return response
