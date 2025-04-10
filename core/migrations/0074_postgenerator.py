# Generated by Django 5.1.4 on 2025-03-04 01:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_businesscontact_followed_alter_decider_followed'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostGenerator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrases', models.TextField(max_length=1000)),
                ('hashtag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.hashtag')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.posttype')),
            ],
        ),
    ]
