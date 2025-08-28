"""
WSGI config for pubsub_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pubsub_project.settings')

application = get_wsgi_application()
