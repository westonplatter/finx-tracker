from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.translation import gettext_lazy as _

from finx_tracker.trades.models import Trade


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

    portfolio = ForeignKey(to=Portfolio, on_delete=models.CASCADE)
    key = models.CharField(max_length=50, blank=False, null=False, default="Unnamed")
    description = models.CharField(max_length=500, blank=True, null=True)


class Grouping(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_grouping"

    class GroupingStatuses(models.TextChoices):
        ACTIVE = "active", _("Active")
        CLOSED = "closed", _("Closed")
        CLOSED_NEW_OPENS = "closed_new_opens", _("Closed to new opening trades")

    name = models.CharField(max_length=50, blank=False, null=False, default="Unnamed")
    strategy = ForeignKey(to=Strategy, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=GroupingStatuses.choices, default=GroupingStatuses.ACTIVE
    )

    trades = models.ManyToManyField(to="trades.Trade", through="portfolios.GroupingTrade")


class GroupingTrade(models.Model):
    class Meta:
        managed = True
        db_table = "portfolios_grouping_trade"

    trade = ForeignKey(
        null=True,
        blank=True,
        to="trades.Trade",
        to_field="trade_id",
        on_delete=models.CASCADE,
    )
    group = ForeignKey(null=True, blank=True, to=Grouping, on_delete=models.CASCADE)


class Position(models.Model):
    class Meta:
        db_table = "portfolios_position"
        managed = False

    originating_transaction_id = models.IntegerField(primary_key=True)

    # portfolio = ForeignKey(to=Portfolio, on_delete=models.CASCADE, to_field='account_id')

    account_id = models.TextField(blank=True, null=True)
    symbol = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    conid = models.IntegerField(blank=False, null=False)

    position = models.IntegerField(blank=True, null=True)
    mark_value = models.FloatField(blank=True, null=True)
    mark_value = models.FloatField(blank=True, null=True)
    open_price = models.FloatField(blank=True, null=True)
    cost_basis = models.FloatField(blank=True, null=True)
    cost_basis_money = models.FloatField(blank=True, null=True)
    fifo_pnl_unrealized = models.FloatField(blank=True, null=True)


    originating_order_id = models.IntegerField(blank=False, null=False)
