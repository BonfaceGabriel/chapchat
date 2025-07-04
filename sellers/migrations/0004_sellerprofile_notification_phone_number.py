# Generated by Django 5.2.1 on 2025-06-16 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellers', '0003_remove_sellerprofile_whatsapp_app_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sellerprofile',
            name='notification_phone_number',
            field=models.CharField(blank=True, help_text="The WhatsApp number (e.g., 2547...) where you'll receive order alerts.", max_length=20, null=True),
        ),
    ]
