# Generated by Django 5.1.4 on 2025-02-05 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_vacancylevel_vacancy_remote_vacancy_salary_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='description',
            field=models.TextField(blank=True, max_length=600, null=True),
        ),
    ]
