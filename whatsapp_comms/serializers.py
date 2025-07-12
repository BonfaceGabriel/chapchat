from rest_framework import serializers
from .models import Conversation, Message, Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["phone_number", "name"]


class ConversationSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "customer", "state", "updated_at", "last_message"]

    def get_last_message(self, obj):
        message = obj.messages.last()
        if message:
            return MessageSerializer(message).data
        return None


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "content", "timestamp"]
        read_only_fields = ["id", "timestamp"]
