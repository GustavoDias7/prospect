# Generated by Django 5.1.4 on 2025-02-28 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_motivationalpost_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='motivationalpost',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
