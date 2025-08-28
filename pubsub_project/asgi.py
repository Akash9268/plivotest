"""
ASGI config for pubsub_project project.
"""

import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pubsub_project.settings')

# Initialize Django
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pubsub.routing import websocket_urlpatterns

# Get the Django ASGI application
django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_app,  # Handle all HTTP requests through Django
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
