# Generated by Django 5.2.1 on 2025-06-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='mpesa_checkout_request_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payments_transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
