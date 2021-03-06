from django.db import models
from django.db.models.fields.related import ForeignKey


class Portfolio(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_portfolio"

    account_id = models.TextField(blank=True, null=True)
    acct_alias = models.FloatField(blank=True, null=True)


# TODO(weston) delete portfolio when a strategy is deleted
def on_delete_callable(*args, **kwargs):
    return None


class Strategy(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_strategy"

    portfolio = ForeignKey(to=Portfolio, on_delete=on_delete_callable)
    name = models.CharField(max_length=50, blank=False, null=False, default="Unnamed")
    description = models.CharField(max_length=500, blank=True, null=True)


class StrategyTrade(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_strategy_trade"

    strategy = ForeignKey(to=Strategy, on_delete=on_delete_callable)
    ext_trade_id = models.BigIntegerField(unique=True, default=-1)
    group_name = models.CharField(max_length=500, blank=True, null=True)
