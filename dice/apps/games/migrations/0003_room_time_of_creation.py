# Generated by Django 3.2.9 on 2022-01-13 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20220109_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='time_of_creation',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]