# Generated by Django 5.1.4 on 2025-03-05 19:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_alter_vacancy_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyHiring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='vacancy',
            name='remote',
        ),
        migrations.AddField(
            model_name='vacancy',
            name='hiring',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.vacancyhiring'),
        ),
    ]
