# Generated by Django 3.2.8 on 2022-06-09 21:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empleoyee', '0010_alter_empleoyee_hiring_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empleoyee',
            name='hiring_date',
            field=models.TextField(default=datetime.date(2022, 6, 9)),
        ),
    ]