# retail_saas/products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    # We can add a read-only field to show the seller's username if needed
    # seller_username = serializers.CharField(source='seller.user.username', read_only=True)

    class Meta:
        model = Product
        # Note: 'seller' is not in this list for creation because we will
        # set it automatically in the view based on the logged-in user.
        # It's a read-only field from the perspective of the API client.
        fields = [
            'id', # Good to include the product ID
            'name',
            'description',
            'sku',
            'price',
            'sizes',
            'images',
            'inventory_count',
            'is_active',
            'created_at',
            'updated_at',
            # 'seller_username',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_sku(self, value):
        """
        Check that the SKU is unique for the current seller.
        This provides more user-friendly validation than the database constraint alone.
        """
        # Get the seller from the context passed by the view
        seller_profile = self.context['request'].user.seller_profile
        
        # On creation, check if a product with this SKU already exists for this seller.
        if self.instance is None: # self.instance is None on create
            if Product.objects.filter(seller=seller_profile, sku=value).exists():
                raise serializers.ValidationError("A product with this SKU already exists.")
        # On update, check if SKU is being changed to one that already exists on another product.
        else:
            if Product.objects.filter(seller=seller_profile, sku=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A product with this SKU already exists.")
        
        return value