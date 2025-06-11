# retail_saas/accounts/migrations/0002_create_initial_superuser.py

from django.db import migrations
from django.conf import settings
import os

def create_superuser(apps, schema_editor):
    """
    Creates a superuser AND their associated SellerProfile if one does not exist,
    using credentials from environment variables.
    """
    # We use apps.get_model to get the historical version of the models
    # to prevent issues with future model changes.
    User = apps.get_model('accounts', 'User')
    SellerProfile = apps.get_model('sellers', 'SellerProfile') # Get the SellerProfile model
    
    SU_USERNAME = os.environ.get('DJANGO_SU_NAME')
    SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL')
    SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD')

    if SU_USERNAME and SU_EMAIL and SU_PASSWORD:
        # Check if the user already exists
        if not User.objects.filter(username=SU_USERNAME).exists():
            print(f"\nCreating superuser: {SU_USERNAME}")
            # Create the superuser
            superuser = User.objects.create_superuser(
                username=SU_USERNAME,
                email=SU_EMAIL,
                password=SU_PASSWORD
            )
            # After creating the user, create their profile
            SellerProfile.objects.create(user=superuser, company_name="Platform Admin")
            print(f"SellerProfile created for superuser: {SU_USERNAME}")
        else:
            # If the user exists, check if they have a profile
            print(f"\nSuperuser {SU_USERNAME} already exists. Checking for profile...")
            try:
                superuser_instance = User.objects.get(username=SU_USERNAME)
                if not SellerProfile.objects.filter(user=superuser_instance).exists():
                    SellerProfile.objects.create(user=superuser_instance, company_name="Platform Admin")
                    print(f"SellerProfile was missing and has now been created for superuser: {SU_USERNAME}")
                else:
                    print("Profile already exists.")
            except User.DoesNotExist:
                pass # Should not happen if the first filter passed, but safe to have.
    else:
        print("\nSuperuser credentials not found in environment. Skipping superuser creation.")


class Migration(migrations.Migration):
    # ... (dependencies remain the same) ...
    dependencies = [
        ('accounts', '0001_initial'),
        # We also depend on the initial migration of the 'sellers' app
        # to ensure the SellerProfile model exists before we try to use it.
        ('sellers', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]