# Generated by Django 5.0.2 on 2024-06-27 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0019_alter_badge_event_alter_badge_member_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
