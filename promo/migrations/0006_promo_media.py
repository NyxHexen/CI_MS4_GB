# Generated by Django 4.1.7 on 2023-03-12 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0018_alter_dlc_media_alter_dlc_tags_alter_game_media_and_more'),
        ('promo', '0005_promo_carousel_promo_featured_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='promo',
            name='media',
            field=models.ManyToManyField(to='games.media'),
        ),
    ]
