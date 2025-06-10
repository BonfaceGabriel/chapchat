# retail_saas/accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email # For email validation
from django.core.exceptions import ValidationError # For email validation

User = get_user_model() # Gets our custom accounts.User model

class UserRegistrationSerializer(serializers.ModelSerializer):
    # We want to write password, but not read it back
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8 # Example: enforce minimum password length
    )
    # This field is only for confirmation during input, not stored
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label='Confirm password', # Label for browsable API forms
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        # Fields that the client will send and that will be used to create the User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'email': {'required': True} # Make email explicitly required
        }

    def validate_email(self, value):
        """
        Check that the email is valid and unique.
        """
        if not value: # Should be caught by required=True, but good to double check
            raise serializers.ValidationError("Email is required.")
        try:
            validate_email(value) # Django's built-in email validator
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        if User.objects.filter(email__iexact=value).exists(): # Case-insensitive check
            raise serializers.ValidationError("A user with that email already exists.")
        return value.lower() # Store emails in lowercase

    # def validate_username(self, value):
    #     """
    #     Check that the username is unique.
    #     """
    #     if User.objects.filter(username__iexact=value).exists(): # Case-insensitive check
    #         raise serializers.ValidationError("A user with that username already exists.")
    #     # Add any other username validation rules here (e.g., length, allowed characters)
    #     return value

    def validate(self, attrs):
        """
        Check that the two password entries match.
        `attrs` is a dictionary of the validated input fields.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        # You can add other cross-field validations here if needed
        return attrs

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        The RetailerProfile will be created automatically by the post_save signal.
        """
        # We don't want to pass password2 to the User.objects.create_user method
        validated_data.pop('password2')
        
        # Use create_user to ensure password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''), # Use .get for optional fields
            last_name=validated_data.get('last_name', '')
        )
        return user