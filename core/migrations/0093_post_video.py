# Generated by Django 5.1.4 on 2025-03-14 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0092_postaudio_post_audio'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
