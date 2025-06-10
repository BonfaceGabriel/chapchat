# retail_saas/products/models.py
from django.db import models
from sellers.models import SellerProfile # Import the SellerProfile model

class Product(models.Model):
    # This is the crucial link for multi-tenancy.
    # Each product belongs to one seller. A seller can have many products.
    # The related_name lets us access products from a seller instance: some_seller.products.all()
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Storing multiple sizes. JSONField is great for this.
    sizes = models.JSONField(default=list, blank=True) # e.g., ["S", "M", "L"] or [{"size": "S", "stock": 10}, ...]

    # Storing multiple images. JSONField works here too for a list of URLs.
    images = models.JSONField(default=list, blank=True) # e.g., ["http://.../img1.png", "http://.../img2.png"]
    
    inventory_count = models.PositiveIntegerField(default=0)
    
    # We'll use is_active for soft deletes instead of actually deleting the record.
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Enforce that the SKU must be unique for each seller.
        # A seller cannot have two products with the same SKU.
        unique_together = ('seller', 'sku')
        ordering = ['-created_at'] # Default ordering for product queries

    def __str__(self):
        return f"{self.name} ({self.seller.user.username})"