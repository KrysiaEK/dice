# Generated by Django 3.2.6 on 2021-09-14 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_alter_game_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='room',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='games.room'),
        ),
    ]
