from django.urls import path
from .views import mpesa_callback

app_name = 'payments'

urlpatterns = [
    path('mpesa-callback/', mpesa_callback, name='mpesa_callback'),
]