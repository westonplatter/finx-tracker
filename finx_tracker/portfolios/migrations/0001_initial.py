# Generated by Django 3.2.13 on 2022-05-14 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.TextField(blank=True, null=True)),
                ('acct_alias', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'portfolios_portfolio',
                'managed': True,
            },
        ),
    ]
