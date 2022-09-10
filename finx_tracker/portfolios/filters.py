from pydoc import describe

import django_filters

from finx_tracker.trades.models import Trade


class TradeListFilterSet(django_filters.FilterSet):
    account_id = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    ungrouped = django_filters.BooleanFilter(field_name="groupings", lookup_expr="isnull", label="Ungrouped?")

    class Meta:
        model = Trade
        fields = ["account_id", "ungrouped", "description"]
