# Generated by Django 4.1 on 2022-08-25 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_activity_intensity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='intensity',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='startLat',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='startLng',
        ),
    ]
