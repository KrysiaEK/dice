# Generated by Django 3.2.12 on 2022-02-25 13:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_room_time_of_creation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='round',
            name='dice1',
        ),
        migrations.RemoveField(
            model_name='round',
            name='dice2',
        ),
        migrations.RemoveField(
            model_name='round',
            name='dice3',
        ),
        migrations.RemoveField(
            model_name='round',
            name='dice4',
        ),
        migrations.RemoveField(
            model_name='round',
            name='dice5',
        ),
        migrations.RemoveField(
            model_name='round',
            name='game',
        ),
        migrations.RemoveField(
            model_name='round',
            name='user',
        ),
        migrations.AlterField(
            model_name='room',
            name='time_of_creation',
            field=models.DateTimeField(default=datetime.datetime(2022, 2, 25, 13, 42, 41, 910273, tzinfo=utc)),
        ),
        migrations.DeleteModel(
            name='Dice',
        ),
        migrations.DeleteModel(
            name='Round',
        ),
    ]
