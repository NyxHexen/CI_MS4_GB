# Generated by Django 4.1.7 on 2023-02-25 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_media_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='media',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
