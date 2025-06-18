import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from sellers.models import SellerProfile # We only need this import for the type check

class InboxConsumer(AsyncWebsocketConsumer):
    # This is an async function, so all DB calls inside must be wrapped
    async def connect(self):
        self.user = self.scope.get('user')
        self.room_group_name = None # Initialize to None

        # Check if the user is authenticated from our middleware
        if self.user is None or not self.user.is_authenticated:
            await self.close()
            return

        # --- THIS IS THE NEW, MORE DIRECT APPROACH ---
        # We will now perform the synchronous DB check within this async method
        # by calling a decorated inner method.
        seller_profile_pk = await self.get_profile_pk()

        if seller_profile_pk is None:
            # If the user has no seller profile, we cannot create a room for them.
            print(f"User {self.user.username} has no seller profile. Closing WebSocket.")
            await self.close()
            return
        
        # Create a unique channel group name for each seller using the PK
        self.room_group_name = f'seller_inbox_{seller_profile_pk}'
        print(f"User {self.user.username} connecting to WebSocket group: {self.room_group_name}")

        # The error was happening here because self.channel_layer was None.
        # This new structure should ensure it is properly initialized.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def get_profile_pk(self):
        """
        This is now a method of the class. It runs in a sync context
        and can safely access the database via self.user.
        """
        try:
            return self.user.seller_profile.pk
        except SellerProfile.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        if self.room_group_name:
            print(f"User {self.user.username} disconnecting from {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({'type': 'echo', 'message': f"You said: {message}"}))
    
    async def new_order_notification(self, event):
        order_data = event['order']
        print(f"Sending 'new_order' notification to group {self.room_group_name}")
        await self.send(text_data=json.dumps({'type': 'new_order', 'payload': order_data}))