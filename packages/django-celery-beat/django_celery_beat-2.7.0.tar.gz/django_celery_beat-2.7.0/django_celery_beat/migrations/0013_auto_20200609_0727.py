# Generated by Django 3.0.6 on 2020-06-09 07:27
# flake8: noqa
from django.db import migrations
import django_celery_beat.models
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0012_periodictask_expire_seconds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crontabschedule',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default=django_celery_beat.models.crontab_schedule_celery_timezone, help_text='Timezone to Run the Cron Schedule on. Default is UTC.', verbose_name='Cron Timezone'),
        ),
    ]
