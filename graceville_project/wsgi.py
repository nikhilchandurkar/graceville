"""
WSGI config for graceville_project project.

It exposes the WSGI callable as a module-level variable named ``application``.
Also exposes ``app`` for Vercel serverless Python runtime.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graceville_project.settings')

application = get_wsgi_application()
app = application

# On Vercel / serverless environments: ensure /tmp/db.sqlite3 tables exist
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    try:
        from django.core.management import call_command
        from django.db import connection
        tables = connection.introspection.table_names()
        if not tables or 'villa_bookinginquiry' not in tables:
            call_command('migrate', interactive=False)
    except Exception:
        pass
