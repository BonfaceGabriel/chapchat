from django.contrib import admin
from .models import SellerProfile

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name')