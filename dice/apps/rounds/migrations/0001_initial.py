# Generated by Django 3.2.12 on 2022-02-25 13:42

import dice.apps.rounds.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0006_auto_20220225_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3)], default=1)),
                ('figure', models.PositiveIntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '3x'), (8, '4x'), (9, '3+2x'), (10, 'Small straight'), (11, 'Large straight'), (12, 'Yatzy'), (13, 'Chance')], null=True)),
                ('points', models.PositiveIntegerField(blank=True, null=True)),
                ('extra_points', models.PositiveIntegerField(default=0)),
                ('dice1', models.OneToOneField(default=dice.apps.rounds.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_first_dice', to='rounds.dice')),
                ('dice2', models.OneToOneField(default=dice.apps.rounds.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_second_dice', to='rounds.dice')),
                ('dice3', models.OneToOneField(default=dice.apps.rounds.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_third_dice', to='rounds.dice')),
                ('dice4', models.OneToOneField(default=dice.apps.rounds.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_fourth_dice', to='rounds.dice')),
                ('dice5', models.OneToOneField(default=dice.apps.rounds.models.Dice.create, on_delete=django.db.models.deletion.CASCADE, related_name='round_as_fifth_dice', to='rounds.dice')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
