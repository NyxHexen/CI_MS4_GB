# Generated by Django 4.1.7 on 2023-03-18 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0018_alter_dlc_media_alter_dlc_tags_alter_game_media_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PegiRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('slug', models.SlugField(max_length=254, null=True)),
                ('image', models.ImageField(null=True, upload_to='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='dlc',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='game',
            name='publisher',
        ),
        migrations.RemoveField(
            model_name='ratingset',
            name='esrb_ratings',
        ),
        migrations.AddField(
            model_name='dlc',
            name='publishers',
            field=models.ManyToManyField(to='games.publisher'),
        ),
        migrations.AddField(
            model_name='game',
            name='publishers',
            field=models.ManyToManyField(to='games.publisher'),
        ),
        migrations.AddField(
            model_name='ratingset',
            name='esrb_rating',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.esrbrating'),
        ),
        migrations.AlterField(
            model_name='developer',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='dlc',
            name='carousel',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='dlc',
            name='featured',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='dlc',
            name='name',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='esrbrating',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='esrbrating',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='platform',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='ratingset',
            name='pegi_rating',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.pegirating'),
        ),
    ]
