# Generated by Django 5.1.4 on 2025-02-09 22:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_company_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='employer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.linkedincontact'),
        ),
    ]
