from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # We inherit username, first_name, last_name, email, password, is_staff, is_active, is_superuser, etc.
    # from AbstractUser.
    # You can add additional fields specific to your retailers here if needed.
    # For example:
    # company_name = models.CharField(max_length=255, blank=True)
    # phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username # Or self.email if you prefer


