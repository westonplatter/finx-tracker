# Generated by Django 3.2.13 on 2022-08-21 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0007_auto_20220526_0548'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Unnamed', max_length=50)),
            ],
            options={
                'db_table': 'portfolios_group',
                'managed': True,
            },
        ),
    ]
