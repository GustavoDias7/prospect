# Generated by Django 5.1.4 on 2025-03-02 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_rename_motivationalpost_post_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VariantPost',
            new_name='PostVariant',
        ),
    ]
