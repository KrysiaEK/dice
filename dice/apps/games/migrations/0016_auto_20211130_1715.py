# Generated by Django 3.2.9 on 2021-11-30 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0015_round_extra_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='round',
            name='extra_points',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='round',
            name='figure',
            field=models.PositiveIntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '3x'), (8, '4x'), (9, '3+2x'), (10, 'Small straight'), (11, 'Large straight'), (12, 'Yatzy'), (13, 'Chance')], null=True),
        ),
    ]
