# Generated by Django 5.1.4 on 2025-03-05 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_vacancyhiring_remove_vacancy_remote_vacancy_hiring'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancy',
            name='link',
        ),
        migrations.AddField(
            model_name='vacancy',
            name='job_view',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
