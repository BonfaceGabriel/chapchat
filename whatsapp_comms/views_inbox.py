from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(seller=self.request.user.seller_profile).order_by('-updated_at')


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        conversation = Conversation.objects.get(pk=self.kwargs['conversation_pk'], seller=self.request.user.seller_profile)
        return conversation.messages.all()

    def perform_create(self, serializer):
        conversation = Conversation.objects.get(pk=self.kwargs['conversation_pk'], seller=self.request.user.seller_profile)
        message = serializer.save(conversation=conversation, sender='seller')

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'seller_inbox_{conversation.seller.pk}',
            {
                'type': 'custom_message',
                'message_type': 'message',
                'message': MessageSerializer(message).data,
            }
        )
