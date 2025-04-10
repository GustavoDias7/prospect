# Generated by Django 5.1.4 on 2025-01-12 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_page_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='not_qualified',
            field=models.BooleanField(default=False, help_text='Account has a website, has been inactive for over a year, or the page is not found.'),
            preserve_default=False,
        ),
    ]
