# Generated by Django 5.1.4 on 2025-03-31 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0113_alter_businesscontact_primary_color_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='audio_url',
            field=models.URLField(blank=True, max_length=400, null=True),
        ),
    ]
