from django.db import models
from django.db.models import Sum, F
from sellers.models import SellerProfile
from whatsapp_comms.models import Customer
from products.models import Product

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress (Cart)'
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pending Payment'
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
        PROCESSING = 'PROCESSING', 'Processing'
        READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready for Pickup'
        OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
        DELIVERED = 'DELIVERED', 'Delivered'
        PICKED_UP = 'PICKED_UP', 'Picked Up'
        CANCELLED = 'CANCELLED', 'Cancelled'
        FAILED = 'FAILED', 'Failed'

    class DeliveryOption(models.TextChoices):
        PICKUP = 'PICKUP', 'Pickup'
        DELIVERY = 'DELIVERY', 'Delivery'

    # Links to the customer and seller
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='orders')

    # Core order details
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.IN_PROGRESS)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Delivery details
    delivery_option = models.CharField(max_length=10, choices=DeliveryOption.choices, blank=True, null=True)
    delivery_address_text = models.TextField(blank=True, null=True)
    delivery_location_coordinates = models.JSONField(default=dict, blank=True)

    # Mpesa payment details
    payments_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} for {self.customer}"

    def update_total(self):
        """Calculates the total amount from all order items."""
        # F() expressions allow you to refer to model field values directly in the database
        # This is more efficient than looping in Python.
        new_total = self.items.aggregate(
            total=Sum(F('quantity') * F('price_at_time_of_purchase'))
        )['total'] or 0.00
        
        self.total_amount = new_total
        self.save()
        print(f"Updated total for Order {self.id} to {self.total_amount}")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    quantity = models.PositiveIntegerField(default=1)
    # Store the price at the time of purchase in case the product's price changes later
    price_at_time_of_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Store chosen size, color, etc.
    selected_size = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"
