"""
WSGI config for dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# Use production settings in production
if os.getenv('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

application = get_wsgi_application()
