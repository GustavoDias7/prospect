# Generated by Django 5.1.4 on 2025-01-19 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_website_whatsapp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='website',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
