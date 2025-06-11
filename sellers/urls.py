from django.urls import path
from .views import SellerProfileDetailView

app_name = 'sellers'

urlpatterns = [
    path('profile/', SellerProfileDetailView.as_view(), name='seller_profile_detail'),
    # We can add more retailer-specific URLs here later (e.g., for products, orders)
]