# Generated by Django 5.1.4 on 2025-02-04 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_alter_company_options_alter_vacancy_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='message',
            field=models.TextField(blank=True, max_length=600, null=True),
        ),
    ]
