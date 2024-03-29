# Generated by Django 4.1.7 on 2023-03-12 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0017_remove_dlc_promo_price_remove_game_promo_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dlc',
            name='media',
            field=models.ManyToManyField(to='games.media'),
        ),
        migrations.AlterField(
            model_name='dlc',
            name='tags',
            field=models.ManyToManyField(to='games.tag'),
        ),
        migrations.AlterField(
            model_name='game',
            name='media',
            field=models.ManyToManyField(to='games.media'),
        ),
        migrations.AlterField(
            model_name='game',
            name='platforms',
            field=models.ManyToManyField(to='games.platform'),
        ),
        migrations.AlterField(
            model_name='game',
            name='tags',
            field=models.ManyToManyField(to='games.tag'),
        ),
    ]
