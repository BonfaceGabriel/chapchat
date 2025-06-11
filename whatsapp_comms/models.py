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
        AWAITING_PRODUCT_QUERY = 'AWAITING_PRODUCT_QUERY', 'Awaiting Product Query'
        # We will add more states like BROWSING_PRODUCTS, IN_CART, etc. later

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