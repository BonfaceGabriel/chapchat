import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from sellers.models import SellerProfile

# Set up logging
logger = logging.getLogger(__name__)

class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        self.room_group_name = None
        
        logger.info(f"WebSocket connection attempt from user: {self.user}")
        
        # Check if the user is authenticated from our middleware
        if self.user is None or not self.user.is_authenticated:
            logger.warning("Unauthenticated user attempted WebSocket connection")
            await self.close()
            return

        # Check if channel_layer is properly configured
        if self.channel_layer is None:
            logger.error("Channel layer is None! Check your CHANNEL_LAYERS configuration.")
            await self.close()
            return

        try:
            # Get the seller profile PK
            seller_profile_pk = await self.get_profile_pk()

            if seller_profile_pk is None:
                logger.warning(f"User {self.user.username} has no seller profile. Closing WebSocket.")
                await self.close()
                return
            
            # Create a unique channel group name for each seller using the PK
            self.room_group_name = f'seller_inbox_{seller_profile_pk}'
            logger.info(f"User {self.user.username} connecting to WebSocket group: {self.room_group_name}")

            # Add to channel group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"WebSocket connection accepted for user {self.user.username}")
            
            # Send a welcome message
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Successfully connected to inbox'
            }))

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            await self.close()

    @database_sync_to_async
    def get_profile_pk(self):
        """
        Get the seller profile PK for the current user.
        Returns None if the user has no seller profile.
        """
        try:
            return self.user.seller_profile.pk
        except SellerProfile.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting seller profile: {str(e)}")
            return None

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        logger.info(f"WebSocket disconnecting with code: {close_code}")
        
        if self.room_group_name and self.channel_layer:
            try:
                logger.info(f"User {self.user.username if self.user else 'Unknown'} disconnecting from {self.room_group_name}")
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                logger.error(f"Error during group discard: {str(e)}")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        """
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            logger.info(f"Received message from {self.user.username}: {message}")
            
            # Echo the message back
            await self.send(text_data=json.dumps({
                'type': 'echo', 
                'message': f"You said: {message}"
            }))
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing received message: {str(e)}")
    
    async def new_order_notification(self, event):
        """
        Called when a new_order_notification event is sent to the group.
        """
        try:
            order_data = event.get('order', {})
            logger.info(f"Sending 'new_order' notification to group {self.room_group_name}")
            
            await self.send(text_data=json.dumps({
                'type': 'new_order', 
                'payload': order_data
            }))
            
        except Exception as e:
            logger.error(f"Error sending new order notification: {str(e)}")

    # You can add more event handlers here as needed
    async def order_status_update(self, event):
        """
        Handle order status update notifications.
        """
        try:
            order_data = event.get('order', {})
            logger.info(f"Sending order status update to group {self.room_group_name}")
            
            await self.send(text_data=json.dumps({
                'type': 'order_status_update',
                'payload': order_data
            }))
            
        except Exception as e:
            logger.error(f"Error sending order status update: {str(e)}")

    async def custom_message(self, event):
        """
        Handle custom messages sent to the group.
        """
        try:
            message = event.get('message', '')
            message_type = event.get('message_type', 'custom')
            
            await self.send(text_data=json.dumps({
                'type': message_type,
                'message': message
            }))
            
        except Exception as e:
            logger.error(f"Error sending custom message: {str(e)}")