# Generated by Django 5.1.4 on 2025-05-08 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0122_interactionflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interactionflow',
            name='contacted',
            field=models.ManyToManyField(blank=True, related_name='contacted_contacts', to='core.businesscontact'),
        ),
        migrations.AlterField(
            model_name='interactionflow',
            name='followed',
            field=models.ManyToManyField(blank=True, related_name='followed_contacts', to='core.businesscontact'),
        ),
        migrations.AlterField(
            model_name='interactionflow',
            name='interacted',
            field=models.ManyToManyField(blank=True, related_name='interacted_contacts', to='core.businesscontact'),
        ),
        migrations.AlterField(
            model_name='interactionflow',
            name='qualified',
            field=models.ManyToManyField(blank=True, related_name='qualified_contacts', to='core.businesscontact'),
        ),
        migrations.AlterField(
            model_name='interactionflow',
            name='responded',
            field=models.ManyToManyField(blank=True, related_name='responded_contacts', to='core.businesscontact'),
        ),
    ]
