from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer # To nest product details
from whatsapp_comms.models import Customer # To get customer details

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone_number', 'name']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) # Nest full product details

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_time_of_purchase', 'selected_size']

class OrderSerializer(serializers.ModelSerializer):
    # Nesting serializers to provide rich data in one API call
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'total_amount', 'delivery_option',
            'delivery_address_text', 'created_at', 'updated_at', 'items'
        ]
        # Make status updatable via PATCH requests
        read_only_fields = ['id', 'customer', 'total_amount', 'created_at', 'updated_at', 'items']