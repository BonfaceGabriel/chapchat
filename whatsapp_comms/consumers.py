import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async # (+) Import the wrapper
from sellers.models import SellerProfile # Import the model to query

# (+) Create an async helper function to fetch the profile
@database_sync_to_async
def get_seller_profile(user):
    """
    Synchronously gets the seller profile for a user but is called asynchronously.
    """
    try:
        return SellerProfile.objects.get(user=user)
    except SellerProfile.DoesNotExist:
        return None


class InboxConsumer(AsyncWebsocketConsumer):
    # This is an async function, so all DB calls inside must be wrapped
    async def connect(self):
        self.user = self.scope.get('user')

        # Check if the user is authenticated
        if self.user is None or not self.user.is_authenticated:
            await self.close()
            return
            
        # --- THE FIX ---
        # Call our new async helper function to safely get the profile from the database.
        self.seller_profile = await get_seller_profile(self.user)

        if self.seller_profile is None:
            # If the user has no seller profile, we cannot create a room for them.
            print(f"User {self.user.username} has no seller profile. Closing WebSocket.")
            await self.close()
            return
            
        # Create a unique channel group name for each seller
        self.room_group_name = f'seller_inbox_{self.seller_profile.pk}'
        print(f"User {self.user.username} connecting to WebSocket group: {self.room_group_name}")

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Use hasattr to safely check if room_group_name was set before disconnecting
        if hasattr(self, 'room_group_name'):
            print(f"User {self.user.username} disconnecting from {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # This function handles messages sent FROM the React client
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(f"Received message from client {self.user.username}: {message}")

        # Echo the message back to the client for now
        await self.send(text_data=json.dumps({
            'type': 'echo',
            'message': f"You said: {message}"
        }))
    
    # This is our custom event handler for broadcasting notifications
    async def new_order_notification(self, event):
        order_data = event['order']
        
        print(f"Sending 'new_order' notification to group {self.room_group_name}")
        # Send the order data to the connected WebSocket client (our React app)
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'payload': order_data
        }))