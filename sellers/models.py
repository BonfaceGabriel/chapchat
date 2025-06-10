from django.db import models
from django.conf import settings # To get the AUTH_USER_MODEL
from django.db.models.signals import post_save # Import post_save
from django.dispatch import receiver # Import receiver

class SellerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True, # Makes the user field the primary key
        related_name='seller_profile'
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    # M-Pesa Credentials (Store these securely! Consider encryption later)
    mpesa_shortcode = models.CharField(max_length=20, blank=True, null=True)
    mpesa_passkey = models.CharField(max_length=100, blank=True, null=True) # Consider encrypted field
    mpesa_consumer_key = models.CharField(max_length=100, blank=True, null=True) # Consider encrypted field
    mpesa_consumer_secret = models.CharField(max_length=100, blank=True, null=True) # Consider encrypted field

    # WhatsApp Configuration
    whatsapp_bsp_api_key = models.CharField(max_length=255, blank=True, null=True) # Consider encrypted field
    whatsapp_phone_number_id = models.CharField(max_length=255, blank=True, null=True) # From BSP
    whatsapp_app_id = models.CharField(max_length=255, blank=True, null=True) # From BSP, if applicable

    # Add other seller-specific settings here as needed
    # e.g., currency, default_language, branding_logo_url, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.company_name or 'No Company Name'})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        SellerProfile.objects.create(user=instance)
        print(f"SellerProfile created for user {instance.username}")
    # If you want to save the profile every time the user is saved (e.g., to update an updated_at field)
    else:
       instance.seller_profile.save()
       print(f"SellerProfile updated for user {instance.username}")
