from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import whatsapp_webhook
from .views_inbox import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

message_list = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('', include(router.urls)),
    path('conversations/<int:conversation_pk>/messages/', message_list, name='message-list'),
]
