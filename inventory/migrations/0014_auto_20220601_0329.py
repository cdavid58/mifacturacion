# Generated by Django 3.2.13 on 2022-06-01 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_shopping_inventory_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopping_inventory',
            name='ico',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='shopping_inventory',
            name='initial_inventory',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='shopping_inventory',
            name='tax',
            field=models.TextField(default=''),
        ),
    ]