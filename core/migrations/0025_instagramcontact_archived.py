# Generated by Django 5.1.4 on 2025-01-28 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_remove_website_last_post_instagramcontact_last_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramcontact',
            name='archived',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
