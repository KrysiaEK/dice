# Generated by Django 3.2.9 on 2022-01-13 12:54

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_alter_room_time_of_creation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='time_of_creation',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 13, 12, 54, 52, 350788, tzinfo=utc)),
        ),
    ]
