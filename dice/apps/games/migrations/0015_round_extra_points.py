# Generated by Django 3.2.6 on 2021-11-02 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_remove_dice_chosen'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='extra_points',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
