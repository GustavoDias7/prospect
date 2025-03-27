# Generated by Django 5.1.4 on 2025-03-26 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0109_remove_decider_svg'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesscontact',
            name='color',
            field=models.CharField(blank=True, choices=[('#64748b', 'slate'), ('#6b7280', 'gray'), ('#71717a', 'zinc'), ('#737373', 'neutral'), ('#78716c', 'stone'), ('#ef4444', 'red'), ('#f97316', 'orange'), ('#f59e0b', 'amber'), ('#eab308', 'yellow'), ('#84cc16', 'lima'), ('#22c55e', 'green'), ('#10b981', 'emerald'), ('#14b8a6', 'teal'), ('#06b6d4', 'cyan'), ('#0ea5e9', 'sky'), ('#3b82f6', 'blue'), ('#6366f1', 'indigo'), ('#8b5cf6', 'violet'), ('#a855f7', 'purple'), ('#d946ef', 'fuchsia'), ('#ec4899', 'pink'), ('#f43f5e', 'rose')], max_length=9, null=True),
        ),
    ]
