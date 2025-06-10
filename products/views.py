# retail_saas/products/views.py
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows retailers to view and manage their products.
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can manage products

    def get_queryset(self):
        """
        This view should return a list of all the products
        for the currently authenticated user.
        """
        # self.request.user is the currently authenticated User instance.
        # self.request.user.seller_profile gets their associated SellerProfile.
        # .products.all() gets all products linked to that profile via the 'related_name'.
        return Product.objects.filter(seller=self.request.user.seller_profile, is_active=True)

    def perform_create(self, serializer):
        """
        Assign the product to the currently authenticated user's seller profile.
        """
        serializer.save(seller=self.request.user.seller_profile)
    
    def get_serializer_context(self):
        """
        Pass the request context to the serializer.
        This is needed for our custom SKU validation.
        """
        return {'request': self.request}

    # By default, ModelViewSet provides 'delete'. We'll override it to do a 'soft delete'.
    def perform_destroy(self, instance):
        """
        Mark the product as inactive instead of deleting it.
        """
        instance.is_active = False
        instance.save()