# Generated by Django 4.1.7 on 2023-04-19 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0031_delete_media_alter_dlc_media_alter_game_media'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developer',
            name='description',
            field=models.TextField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='platform',
            name='description',
            field=models.TextField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='description',
            field=models.TextField(default='', max_length=500),
        ),
    ]
