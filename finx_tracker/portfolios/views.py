from typing import Any, Dict, List, T

import django_filters.views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Window
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView, CreateView

from finx_tracker.portfolios.aggregate_queries import agg_query_strategy_pnl
from finx_tracker.portfolios.filters import TradeListFilterSet
from finx_tracker.portfolios.forms import TradeForm, GroupingFormSet
from finx_tracker.portfolios.models import Grouping, Portfolio, Position, Strategy
from finx_tracker.trades.models import Trade


class PortfolioDetailView(LoginRequiredMixin, DetailView):
    # https://docs.djangoproject.com/en/4.1/ref/class-based-views/generic-display/#detailview
    model = Portfolio
    slug_field = "portfolio_id"
    slug_url_kwarg = "portfolio_id"


class PortfolioListView(LoginRequiredMixin, ListView):
    # https://docs.djangoproject.com/en/4.1/ref/class-based-views/generic-display/#listview
    model = Portfolio
    paginate_by = 10
    ordering = ["account_id"]


class PortfolioPnlView(LoginRequiredMixin, ListView):
    template_name: str = "portfolios/portfolio_pnl.html"

    def get_queryset(self):
        return agg_query_strategy_pnl()


class TradeListView(LoginRequiredMixin, django_filters.views.FilterView):
    model = Trade
    template_name = "portfolios/trade_list.html"
    paginate_by = 100
    filterset_class = TradeListFilterSet
    ordering = ["-date_time"]

    def get_queryset(self) -> QuerySet[T]:
        qs = super().get_queryset()  # to work with django-filters
        qs = qs.filter()  # TODO qs = qs.filter(user=self.request.user)
        qs = qs.prefetch_related("groupings")
        return qs


class TradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Trade
    template_name = "portfolios/trade_form.html"
    slug_field = "trade_id"
    slug_url_kwarg = "trade_id"
    success_url = reverse_lazy("portfolios:trade-list")
    form_class = TradeForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["grouping_id_choices"] = self.possible_group_ids(self.object.account_id)
        return kwargs

    @staticmethod
    def possible_group_ids(account_id: str) -> List[str]:
        qs = Grouping.objects.filter(strategy__portfolio__account_id=account_id)
        return qs.values("id")


class GroupingListView(LoginRequiredMixin, ListView):
    model = Grouping
    template_name = "portfolios/grouping_list.html"
    paginate_by = 100

    def get_queryset(self) -> QuerySet[T]:
        qs = super().get_queryset()
        qs = qs.prefetch_related("strategy__portfolio")
        qs = qs.order_by("strategy__portfolio__account_id", "status", "name")
        return qs


class GroupingDetailView(LoginRequiredMixin, DetailView):
    model = Grouping
    template_name = "groupings/grouping_detail.html"

    def get_trade_list(self):
        return (
            Trade.objects.prefetch_related("groupings")
            .filter(groupings=self.object)
            .annotate(
                fifo_pnl_realized_cumsum=Window(Sum("fifo_pnl_realized"), order_by=F("date_time").asc())
            )
            .all()
            .order_by("-date_time")
        )

    def get_position_list(self):
        transaction_ids = Trade.objects.filter(groupings=self.object).values_list("transaction_id", flat=True)

        return (
            Position.objects.prefetch_related("groupings")
            .filter(originating_transaction_id__in=transaction_ids)
            .values("conid", "symbol", "description", "fifo_pnl_unrealized", "position", "mark_price")
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data["trade_list"] = self.get_trade_list()
        context_data["position_list"] = self.get_position_list()
        return context_data



class StrategyCreateView(LoginRequiredMixin, CreateView):
    model = Strategy
    fields = ["key", "description", "portfolio"]
    template_name: str = "portfolios/strategy_form.html"

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["name"] = None
        return initial

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["groupings"] = GroupingFormSet(self.request.POST)
        else:
            data["groupings"] = GroupingFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        groupings = context["groupings"]
        self.object = form.save()
        if groupings.is_valid():
            groupings.instance = self.object
            groupings.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("portfolios:grouping-list")

