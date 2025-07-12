from django.db import models
from sellers.models import SellerProfile

class Customer(models.Model):
    phone_number = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.phone_number

class Conversation(models.Model):
    class ConversationState(models.TextChoices):
        STARTED = 'STARTED', 'Started'
        AWAITING_COMMAND = 'AWAITING_COMMAND', 'Awaiting Command'
        AWAITING_PRODUCT_SELECTION = 'AWAITING_PRODUCT_SELECTION', 'Awaiting Product Selection'
        AWAITING_PRODUCT_ACTION = 'AWAITING_PRODUCT_ACTION', 'Awaiting Product Action'
        AWAITING_SIZE_SELECTION = 'AWAITING_SIZE_SELECTION', 'Awaiting Size Selection'  
        AWAITING_QUANTITY = 'AWAITING_QUANTITY', 'Awaiting Quantity'
        VIEWING_CART = 'VIEWING_CART', 'Viewing Cart'
        AWAITING_DELIVERY_CHOICE = 'AWAITING_DELIVERY_CHOICE', 'Awaiting Delivery Choice'   
        AWAITING_DELIVERY_ADDRESS = 'AWAITING_DELIVERY_ADDRESS', 'Awaiting Delivery Address'    
        AWAITING_PAYMENT_CONFIRMATION = 'AWAITING_PAYMENT_CONFIRMATION', 'Awaiting Payment Confirmation'    

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='conversations')
    state = models.CharField(
        max_length=30,
        choices=ConversationState.choices,
        default=ConversationState.STARTED
    )
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'seller')

    def __str__(self):
        return f"Conversation with {self.customer} for {self.seller.user.username} - State: {self.get_state_display()}"


class Message(models.Model):
    """Stores individual chat messages for a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(
        max_length=10,
        choices=[("customer", "Customer"), ("seller", "Seller"), ("bot", "Bot")],
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender} at {self.timestamp:%Y-%m-%d %H:%M}: {self.content[:20]}"