# Generated by Django 3.2.13 on 2022-09-03 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0002_alter_trade_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trade',
            options={'managed': True},
        ),
    ]