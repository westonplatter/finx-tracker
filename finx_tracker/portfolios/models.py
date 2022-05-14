from django.db import models
from django.db.models.fields.related import ForeignKey


class Portfolio(models.Model):
    class Meta:
        managed = True
        db_table = 'portfolios_portfolio'

    account_id = models.TextField(blank=True, null=True)
    acct_alias = models.FloatField(blank=True, null=True)


def on_delete_callable(*args, **kwargs):
    return None


class Strategy(models.Model):
    class Meta:
        managed = True
        db_table = 'portfolios_strategy'

    portfolio = ForeignKey(to=Portfolio, on_delete=on_delete_callable)
    acct_alias = models.FloatField(blank=True, null=True)
