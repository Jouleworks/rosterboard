# Generated by Django 5.0.2 on 2024-05-25 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0015_remove_event_publickey'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceKiosk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('single_state_only', models.BooleanField(default=False)),
                ('automated_check_in_out', models.BooleanField(default=False)),
                ('allow_status_selection', models.BooleanField(default=False)),
                ('allow_duty_selection', models.BooleanField(default=False)),
                ('check_in_duty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_in_duty', to='roster.duty')),
                ('check_in_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_in_status', to='roster.status')),
                ('check_out_duty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_out_duty', to='roster.duty')),
                ('check_out_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='check_out_status', to='roster.status')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roster.event')),
            ],
        ),
    ]
