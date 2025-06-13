from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'seller', 'status', 'total_amount', 'created_at', 'updated_at', 'delivery_address_text', 'delivery_option', 'delivery_location_coordinates')
    list_filter = ('status', 'seller', 'created_at')
    search_fields = ('customer__phone_number', 'seller__user__username')
    readonly_fields = ('total_amount',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_time_of_purchase')
    list_filter = ('order__status', 'product')
    search_fields = ('order__customer__phone_number', 'product__name')
    readonly_fields = ('price_at_time_of_purchase',)