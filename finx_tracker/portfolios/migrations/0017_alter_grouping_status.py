# Generated by Django 3.2.13 on 2022-08-24 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0016_grouping_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouping',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('closed', 'Closed'), ('closed_new_opens', 'Closed to new opening trades')], default='active', max_length=16),
        ),
    ]
