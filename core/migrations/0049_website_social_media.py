# Generated by Django 5.1.4 on 2025-02-23 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_rename_phone_instagramcontact_cellphone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='social_media',
            field=models.BooleanField(default=False),
        ),
    ]
