# Generated by Django 3.2.8 on 2022-06-09 21:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_auto_20200603_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='date_register',
            field=models.TextField(default=datetime.date(2022, 6, 9)),
        ),
        migrations.AlterField(
            model_name='company',
            name='payment_date',
            field=models.TextField(default=datetime.date(2022, 6, 9)),
        ),
    ]
