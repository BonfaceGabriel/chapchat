from django.contrib import admin
from .models import Customer, Conversation

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name', 'created_at')
    search_fields = ('phone_number', 'name')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'seller', 'state', 'updated_at')
    list_filter = ('state', 'seller')
    search_fields = ('customer__phone_number', 'seller__user__username')
