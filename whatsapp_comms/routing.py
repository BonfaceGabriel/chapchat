from django.urls import re_path
from . import consumers 

websocket_urlpatterns = [
    # re_path is used for regular expression URL matching.
    # This pattern will match URLs like ws://.../ws/inbox/
    re_path(r'ws/inbox/$', consumers.InboxConsumer.as_asgi()),
]