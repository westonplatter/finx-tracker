# Generated by Django 3.2.13 on 2022-09-03 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0024_grouping_trades'),
        ('trades', '0004_alter_trade_trade_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='groupings',
            field=models.ManyToManyField(through='portfolios.GroupingTrade', to='portfolios.Grouping'),
        ),
    ]
