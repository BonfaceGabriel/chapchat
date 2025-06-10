from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product') # Register products at the root of this app's URLs

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]