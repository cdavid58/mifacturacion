# Generated by Django 3.2.13 on 2022-05-31 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_shopping_inventory_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopping_inventory',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
