# Generated by Django 5.1.4 on 2025-03-13 22:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_remove_postgenerator_variant_postgenerator_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='square_area',
            new_name='width',
        ),
    ]
