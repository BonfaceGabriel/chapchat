import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core_backend.middleware import TokenAuthMiddleware
import whatsapp_comms.routing

# This line MUST be at the top, before other Django imports that need settings.


# The 'application' variable must be defined at the end, after all necessary imports.
application = ProtocolTypeRouter({
    # We define the HTTP handler first as a default.
    # get_asgi_application() will find the default Django routing.
    "http": get_asgi_application(),

    # WebSocket requests are handled by our custom middleware and routing.
    "websocket": TokenAuthMiddleware(
        URLRouter(
            whatsapp_comms.routing.websocket_urlpatterns
        )
    ),
})