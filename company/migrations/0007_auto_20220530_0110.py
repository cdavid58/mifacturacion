# Generated by Django 3.2.13 on 2022-05-30 01:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0006_auto_20220525_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='date_register',
            field=models.TextField(default=datetime.date(2022, 5, 30)),
        ),
        migrations.AlterField(
            model_name='company',
            name='payment_date',
            field=models.TextField(default=datetime.date(2022, 5, 30)),
        ),
    ]
