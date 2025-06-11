
from rest_framework import serializers
from .models import SellerProfile
from accounts.serializers import UserRegistrationSerializer # We might want to show some basic user details

class SellerProfileSerializer(serializers.ModelSerializer):
    # You might want to show some read-only user details from the related User model
    # Or even make some User fields writable through the profile endpoint (less common)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    # If you want to allow updating user's email or first/last name via profile:
    # email = serializers.EmailField(source='user.email') # Would require custom update logic
    # first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    # last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)


    class Meta:
        model = SellerProfile
        # Fields from SellerProfile that the Seller can view and update
        # `user` field is the PK and is implicitly handled by the instance.
        fields = [
            'username', # Read-only from User model
            'email',    # Read-only from User model
            # 'first_name', # If you make user fields writable
            # 'last_name',  # If you make user fields writable
            'company_name',
            'mpesa_shortcode',
            'mpesa_passkey',
            'mpesa_consumer_key',
            'mpesa_consumer_secret',
            'whatsapp_phone_number_id',
            'created_at', # Read-only
            'updated_at'  # Read-only
        ]
        read_only_fields = ('user', 'created_at', 'updated_at', 'username', 'email') # user is PK and shouldn't be changed via API
        # If you make user fields like email, first_name, last_name writable, remove them from read_only_fields
        # and handle their update in the view or serializer's update() method.

    # If you allow updating related User fields like email, first_name, last_name:
    # def update(self, instance, validated_data):
    #     user_data = validated_data.pop('user', {}) # Extract user data if present
    #     user = instance.user

    #     # Update User model fields
    #     user.email = user_data.get('email', user.email)
    #     user.first_name = user_data.get('first_name', user.first_name)
    #     user.last_name = user_data.get('last_name', user.last_name)
    #     user.save()

    #     # Update SellerProfile fields
    #     # This is the default behavior of ModelSerializer.update()
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance