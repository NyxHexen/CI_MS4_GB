# Generated by Django 4.1.7 on 2023-03-11 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0017_remove_dlc_promo_price_remove_game_promo_price_and_more'),
        ('promo', '0004_remove_promo_apply_to_promo_apply_to_dlc_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='promo',
            name='carousel',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='promo',
            name='is_featured',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='promo',
            name='apply_to_dlc',
            field=models.ManyToManyField(blank=True, related_name='mtm', to='games.dlc'),
        ),
    ]
