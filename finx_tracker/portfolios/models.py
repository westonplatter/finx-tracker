from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.translation import gettext_lazy as _


# TODO(weston) delete portfolio when a strategy is deleted
def on_delete_callable(*args, **kwargs):
    return None


class Portfolio(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_portfolio"

    account_id = models.TextField(blank=True, null=True)
    acct_alias = models.FloatField(blank=True, null=True)


class Strategy(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_strategy"

    portfolio = ForeignKey(to=Portfolio, on_delete=on_delete_callable)
    key = models.CharField(max_length=50, blank=False, null=False, default="Unnamed")
    description = models.CharField(max_length=500, blank=True, null=True)

class Grouping(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_grouping"

    class GroupingStatuses(models.TextChoices):
        ACTIVE = 'active', _('Active')
        CLOSED = 'closed', _('Closed')
        CLOSED_NEW_OPENS = 'closed_new_opens', _('Closed to new opening trades')

    name = models.CharField(max_length=50, blank=False, null=False, default="Unnamed")
    strategy = ForeignKey(to=Strategy, on_delete=on_delete_callable, null=True, blank=True)
    status = models.CharField(max_length=16, choices=GroupingStatuses.choices, default=GroupingStatuses.ACTIVE)


class GroupingTrade(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_grouping_trade"

    ext_trade_id = models.BigIntegerField(unique=True, default=-1)
    group = ForeignKey(null=True, blank=True, to=Grouping, on_delete=on_delete_callable)



class Position(models.Model):
    class Meta:
        db_table = "portfolios_position"

    portfolio = ForeignKey(to=Portfolio, on_delete=on_delete_callable)
    conid = models.IntegerField(blank=False, null=False)
    quantity = models.IntegerField(blank=False, null=False)
    closing_value = models.FloatField(blank=True, null=True)

