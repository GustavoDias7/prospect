# Generated by Django 5.1.4 on 2025-03-16 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_remove_post_height_post_aspect_ratio_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='aspect_ratio_image',
            field=models.CharField(blank=True, choices=[('9:16', '9:16'), ('4:5', '4:5'), ('3:4', '3:4'), ('1:1', '1:1')], default='3:4', max_length=4, null=True),
        ),
    ]
