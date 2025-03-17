# Generated by Django 5.1.4 on 2025-03-15 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_rename_background_image1_post_image1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='aspect_ratio_image1',
            field=models.CharField(blank=True, choices=[('16_9', '16:9'), ('9_16', '9:16'), ('4_3', '4:3'), ('3_4', '3:4'), ('1_1', '1:1')], default='4_3', max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='aspect_ratio_image2',
            field=models.CharField(blank=True, choices=[('16_9', '16:9'), ('9_16', '9:16'), ('4_3', '4:3'), ('3_4', '3:4'), ('1_1', '1:1')], default='4_3', max_length=4, null=True),
        ),
    ]
