# Generated by Django 5.1.4 on 2025-03-18 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0099_alter_post_aspect_ratio_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='font_size',
            field=models.PositiveSmallIntegerField(default=48),
        ),
        migrations.AlterField(
            model_name='post',
            name='text_wrap',
            field=models.PositiveSmallIntegerField(default=40),
        ),
    ]
