# Generated by Django 3.2.8 on 2022-05-06 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empleoyee', '0001_initial'),
        ('client', '0001_initial'),
        ('data', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='POS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.TextField()),
                ('prefix', models.TextField()),
                ('code', models.TextField()),
                ('quanty', models.TextField()),
                ('description', models.TextField()),
                ('price', models.TextField()),
                ('tax', models.TextField()),
                ('notes', models.TextField()),
                ('date', models.TextField()),
                ('ipo', models.TextField()),
                ('discount', models.TextField()),
                ('type', models.TextField(default='FE')),
                ('state', models.TextField(default=110001)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.client')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('empleoyee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='empleoyee.empleoyee')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet_POS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.TextField()),
                ('date', models.TextField()),
                ('paid_out', models.BooleanField(default=False)),
                ('days_past_due', models.IntegerField(default=0)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.client')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('pos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.pos')),
            ],
        ),
        migrations.CreateModel(
            name='Payment_Form_Invoice_POS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_due_date', models.TextField()),
                ('duration_measure', models.TextField()),
                ('payment_form_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.payment_form')),
                ('payment_method_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.payment_method')),
                ('pos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.pos')),
            ],
        ),
        migrations.CreateModel(
            name='History_Invoice_POS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.TextField()),
                ('time', models.TextField()),
                ('empleoyee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empleoyee.empleoyee')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.wallet_pos')),
            ],
        ),
        migrations.CreateModel(
            name='Credit_Note_POS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.TextField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company')),
                ('pos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pos.pos')),
            ],
        ),
    ]