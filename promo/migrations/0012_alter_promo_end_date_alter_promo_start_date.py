# Generated by Django 4.1.7 on 2023-03-31 17:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo', '0011_alter_promo_end_date_alter_promo_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promo',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 1, 0, 1), null=True),
        ),
        migrations.AlterField(
            model_name='promo',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 31, 0, 1), null=True),
        ),
    ]