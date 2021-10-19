# Generated by Django 3.2.6 on 2021-10-12 16:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0011_auto_20210921_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='round',
            name='figure',
            field=models.PositiveIntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '3x'), (8, '4x'), (25, '3+2x'), (30, 'Small straight'), (40, 'Large straight'), (50, 'Yatzy'), (100, 'Chance')], null=True),
        ),
    ]