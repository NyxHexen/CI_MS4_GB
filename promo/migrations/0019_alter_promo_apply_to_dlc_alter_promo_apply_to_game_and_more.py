# Generated by Django 4.1.7 on 2023-04-16 10:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0030_alter_userrating_value'),
        ('promo', '0018_alter_promo_end_date_alter_promo_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo',
            name='apply_to_dlc',
            field=models.ManyToManyField(blank=True, related_name='dlcset', to='games.dlc'),
        ),
        migrations.AlterField(
            model_name='promo',
            name='apply_to_game',
            field=models.ManyToManyField(blank=True, related_name='gameset', to='games.game'),
        ),
        migrations.AlterField(
            model_name='promo',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 17, 0, 1), null=True),
        ),
        migrations.AlterField(
            model_name='promo',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 16, 0, 1), null=True),
        ),
    ]
