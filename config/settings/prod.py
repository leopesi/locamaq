"""
LocaMaq — Production settings.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF - allow non-HTTPS in production (no SSL yet)
CSRF_TRUSTED_ORIGINS = [
    'http://76.13.66.202',
    'http://localhost',
]

# Static files served by Nginx in production
STATIC_ROOT = BASE_DIR / 'staticfiles'
