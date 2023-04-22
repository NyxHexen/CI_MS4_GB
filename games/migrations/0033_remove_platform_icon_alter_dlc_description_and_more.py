# Generated by Django 4.1.7 on 2023-04-22 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0032_alter_developer_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platform',
            name='icon',
        ),
        migrations.AlterField(
            model_name='dlc',
            name='description',
            field=models.TextField(default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='game',
            name='description',
            field=models.TextField(default='', max_length=1024),
        ),
    ]