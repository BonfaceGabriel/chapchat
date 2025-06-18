import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from sellers.models import SellerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_seller_profile_pk_from_user(user):
    """
    Safely fetches the primary key of the SellerProfile linked to a user.
    This function contains all the synchronous database access.
    """
    if not user or not user.is_authenticated:
        return None
    try:
        # Accessing .seller_profile directly here is safe because this
        # entire function is wrapped and runs in a synchronous context.
        return user.seller_profile.pk
    except SellerProfile.DoesNotExist:
        return None

class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.scope['user'] is populated by our TokenAuthMiddleware
        self.user = self.scope.get('user')

        if self.user is None or not self.user.is_authenticated:
            await self.close()
            return
        
        # --- THE DEFINITIVE FIX ---
        # Call our async helper to safely get the profile's primary key
        seller_profile_pk = await get_seller_profile_pk_from_user(self.user)

        if seller_profile_pk is None:
            # If the user has no seller profile, we cannot create a room.
            print(f"User {self.user.username} has no seller profile. Closing WebSocket.")
            await self.close()
            return
        
        # Create a unique channel group name for each seller using the PK
        self.room_group_name = f'seller_inbox_{seller_profile_pk}'
        print(f"User {self.user.username} connecting to WebSocket group: {self.room_group_name}")

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            print(f"User {self.user.username} disconnecting from {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # This function remains the same
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({'type': 'echo', 'message': f"You said: {message}"}))
    
    async def new_order_notification(self, event):
        # This function remains the same
        order_data = event['order']
        print(f"Sending 'new_order' notification to group {self.room_group_name}")
        await self.send(text_data=json.dumps({'type': 'new_order', 'payload': order_data}))