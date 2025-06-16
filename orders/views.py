from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows retailers to view and manage their orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options'] # Allow list, retrieve, and partial_update

    def get_queryset(self):
        """
        This view should return a list of all the orders
        for the currently authenticated seller's profile.
        We exclude 'IN_PROGRESS' orders as those are carts.
        """
        return Order.objects.filter(seller=self.request.user.seller_profile)\
                            .exclude(status=Order.OrderStatus.IN_PROGRESS)\
                            .order_by('-created_at')

    def perform_update(self, serializer):
        # We can add logic here later to trigger notifications on status change
        # For now, just save the update.
        serializer.save()