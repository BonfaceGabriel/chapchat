import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack # For getting user in consumer
from core_backend.middleware import TokenAuthMiddleware
import whatsapp_comms.routing 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')

# This is the standard Django ASGI app for handling regular HTTP requests
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # For regular HTTP requests, use Django's default ASGI app.
    "http": django_asgi_app,

    # For WebSocket requests, use our authentication stack and URL router.
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         whatsapp_comms.routing.websocket_urlpatterns
    #     )
    # ),

    "websocket": TokenAuthMiddleware(
        URLRouter(
            whatsapp_comms.routing.websocket_urlpatterns
        )
    ),
})