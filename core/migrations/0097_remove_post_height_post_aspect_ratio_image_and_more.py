# Generated by Django 5.1.4 on 2025-03-16 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0096_post_aspect_ratio_image1_post_aspect_ratio_image2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='height',
        ),
        migrations.AddField(
            model_name='post',
            name='aspect_ratio_image',
            field=models.CharField(blank=True, choices=[('16:9', '16:9'), ('9:16', '9:16'), ('5:4', '5:4'), ('4:5', '4:5'), ('4:3', '4:3'), ('3:4', '3:4'), ('1:1', '1:1')], default='9:16', max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='aspect_ratio_image1',
            field=models.CharField(blank=True, choices=[('16:9', '16:9'), ('9:16', '9:16'), ('5:4', '5:4'), ('4:5', '4:5'), ('4:3', '4:3'), ('3:4', '3:4'), ('1:1', '1:1')], default='4:3', max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='aspect_ratio_image2',
            field=models.CharField(blank=True, choices=[('16:9', '16:9'), ('9:16', '9:16'), ('5:4', '5:4'), ('4:5', '4:5'), ('4:3', '4:3'), ('3:4', '3:4'), ('1:1', '1:1')], default='4:3', max_length=4, null=True),
        ),
    ]
