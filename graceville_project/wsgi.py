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

# On Vercel / serverless environments: ensure /tmp/db.sqlite3 tables exist and superuser is configured
if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    try:
        from django.core.management import call_command
        from django.db import connection
        tables = connection.introspection.table_names()
        if not tables or 'villa_bookinginquiry' not in tables:
            call_command('migrate', interactive=False)

        # Allow rotating / initializing admin credentials securely via environment variables
        su_user = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        su_pass = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        su_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@graceville.in')
        if su_user and su_pass:
            from django.contrib.auth.models import User
            u, _ = User.objects.get_or_create(
                username=su_user,
                defaults={'email': su_email, 'is_staff': True, 'is_superuser': True}
            )
            u.set_password(su_pass)
            u.is_staff = True
            u.is_superuser = True
            u.save()
    except Exception:
        pass

