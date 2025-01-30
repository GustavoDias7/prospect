# Generated by Django 5.1.4 on 2025-01-16 18:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_contact_not_qualified_contact_qualified'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('username', models.CharField(blank=True, max_length=30, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=13, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('qualified', models.BooleanField(blank=True, default=None, help_text='Account has a website, has been inactive for an extended period, or the page is not found.', null=True)),
                ('decider', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.decider')),
            ],
        ),
    ]
