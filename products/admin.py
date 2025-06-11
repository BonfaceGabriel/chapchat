from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'sku', 'price', 'inventory_count', 'is_active')
    list_filter = ('is_active', 'seller')
    search_fields = ('name', 'sku', 'seller__user__username')
