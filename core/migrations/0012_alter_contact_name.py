# Generated by Django 5.1.4 on 2025-01-13 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_rename_path_query_contact_facebook_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
