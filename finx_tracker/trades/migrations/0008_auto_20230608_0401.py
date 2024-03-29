# Generated by Django 3.2.13 on 2023-06-08 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0007_auto_20230607_0421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='orig_trade_date',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='orig_trade_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='trader_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='volatility_order_link',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='when_realized',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='when_reopened',
            field=models.TextField(blank=True, null=True),
        ),
    ]
