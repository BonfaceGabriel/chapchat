from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # You can customize the admin interface for your User model here if needed
    # For example, add custom fields to list_display or fieldsets
    # model = User
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    pass # For now, default UserAdmin is fine

admin.site.register(User, CustomUserAdmin)
