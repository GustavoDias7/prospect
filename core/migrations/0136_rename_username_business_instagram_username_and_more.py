# Generated by Django 5.1.4 on 2025-05-14 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0135_staffmember_facebook_alter_staffmember_observation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='business',
            old_name='username',
            new_name='instagram_username',
        ),
        migrations.AddField(
            model_name='business',
            name='facebook_username',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
