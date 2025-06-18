import json
from channels.generic.websocket import AsyncWebsocketConsumer

class InboxConsumer(AsyncWebsocketConsumer):
    # This function is called when a WebSocket connection is initiated.
    async def connect(self):
        # `self.scope` is like the `request` object in Django views.
        # It contains information about the connection, including the user.
        self.user = self.scope['user']

        # --- Check if the user is authenticated ---
        if not self.user.is_authenticated:
            # If the user is not logged in, reject the connection.
            await self.close()
            return

        # --- Create a unique channel group name for each seller ---
        # We want to send notifications only to the relevant seller.
        # `self.user.seller_profile.pk` gets the primary key of the logged-in seller's profile.
        self.room_group_name = f'seller_inbox_{self.user.seller_profile.pk}'
        print(f"User {self.user.username} connecting to WebSocket group: {self.room_group_name}")

        # Join the room group.
        # `self.channel_layer.group_add` adds this specific user's connection
        # to a group that we can broadcast messages to later.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection. This must be the last call in `connect`.
        await self.accept()

    # This function is called when the WebSocket connection is closed.
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            print(f"User {self.user.username} disconnecting from {self.room_group_name}")
            # Leave the room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # This function is called when we receive a message FROM the WebSocket client (the React app).
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(f"Received message from client {self.user.username}: {message}")

        # For now, just echo the message back to the client
        await self.send(text_data=json.dumps({
            'message': f"You said: {message}"
        }))
    
    # This is a custom event handler. We will call this from our M-Pesa callback view
    # to send a 'new_order' event TO the React app.
    async def new_order_notification(self, event):
        order_data = event['order']
        
        print(f"Sending 'new_order' notification to group {self.room_group_name}")
        # Send the order data to the WebSocket client.
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'payload': order_data
        }))