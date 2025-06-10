from django.urls import path
from .views import UserRegistrationView

# accounts/urls.py
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    ]

