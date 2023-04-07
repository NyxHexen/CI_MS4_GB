# Generated by Django 4.1.7 on 2023-04-07 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('games', '0022_feature_rename_featured_dlc_is_featured_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(choices=[(1, 'Dislike'), (2, 'Meh'), (3, 'Neutral'), (4, 'Like'), (5, 'Love')])),
                ('rating_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.ratingset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'rating_set')},
            },
        ),
    ]