# Generated by Django 3.2.13 on 2022-05-31 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_shopping_inventory_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='supplier',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier'),
        ),
    ]
