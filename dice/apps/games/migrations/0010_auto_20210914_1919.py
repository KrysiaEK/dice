# Generated by Django 3.2.6 on 2021-09-14 17:19

import dice.apps.games.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0009_auto_20210914_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='dice1',
            field=models.OneToOneField(default=dice.apps.games.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_first_dice', to='games.dice'),
        ),
        migrations.AlterField(
            model_name='round',
            name='dice2',
            field=models.OneToOneField(default=dice.apps.games.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_second_dice', to='games.dice'),
        ),
        migrations.AlterField(
            model_name='round',
            name='dice3',
            field=models.OneToOneField(default=dice.apps.games.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_third_dice', to='games.dice'),
        ),
        migrations.AlterField(
            model_name='round',
            name='dice4',
            field=models.OneToOneField(default=dice.apps.games.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_fourth_dice', to='games.dice'),
        ),
        migrations.AlterField(
            model_name='round',
            name='dice5',
            field=models.OneToOneField(default=dice.apps.games.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_fifth_dice', to='games.dice'),
        ),
    ]