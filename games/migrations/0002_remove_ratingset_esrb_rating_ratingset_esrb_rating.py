# Generated by Django 4.1.7 on 2023-02-24 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratingset',
            name='esrb_rating',
        ),
        migrations.AddField(
            model_name='ratingset',
            name='esrb_rating',
            field=models.ManyToManyField(to='games.esrbrating'),
        ),
    ]
