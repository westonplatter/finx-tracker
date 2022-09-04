from typing import Any, Dict, List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView
from django.db.models import F, Sum, Window


from finx_tracker.portfolios.aggregate_queries import agg_query_strategy_pnl
from finx_tracker.portfolios.models import Portfolio, Grouping
from finx_tracker.portfolios.forms import TradeForm
from finx_tracker.trades.models import Trade



class PortfolioDetailView(LoginRequiredMixin, DetailView):
    # https://docs.djangoproject.com/en/4.1/ref/class-based-views/generic-display/#detailview
    model = Portfolio
    slug_field = "portfolio_id"
    slug_url_kwarg = "portfolio_id"


portfolio_detail_view = PortfolioDetailView.as_view()


class PortfolioListView(LoginRequiredMixin, ListView):
    # https://docs.djangoproject.com/en/4.1/ref/class-based-views/generic-display/#listview
    model = Portfolio
    paginate_by = 100  # if pagination is desired


portfolio_list_view = PortfolioListView.as_view()


class PortfolioPnlView(LoginRequiredMixin, ListView):
    template_name: str = "portfolios/portfolio_pnl.html"

    def get_queryset(self):
        return agg_query_strategy_pnl()


portfolio_pnl_view = PortfolioPnlView.as_view()


class TradeListView(LoginRequiredMixin, ListView):
    model = Trade
    template_name = "portfolios/trade_list.html"
    paginate_by = 50

    def get_queryset(self):
        return (super()
            .get_queryset()
            .prefetch_related("groupings")
            .order_by("-date_time")
        )

trade_list_view = TradeListView.as_view()

class TradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Trade
    slug_field = "trade_id"
    slug_url_kwarg = "trade_id"
    success_url = reverse_lazy("portfolios:trades-list")
    form_class = TradeForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["grouping_id_choices"] = self.possible_group_ids(self.object.account_id)
        return kwargs

    @staticmethod
    def possible_group_ids(account_id: str) -> List[str]:
        qs = Grouping.objects.filter(strategy__portfolio__account_id=account_id)
        return qs.values("id")

trade_update_view = TradeUpdateView.as_view()


class GroupingDetailView(LoginRequiredMixin, DetailView):
    model = Grouping
    template_name = "groupings/grouping_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context_data = super().get_context_data(**kwargs)

        trade_list = (Trade.objects
            .prefetch_related("groupings")
            .filter(groupings=self.object)
            .annotate(fifo_pnl_realized_cumsum=Window(Sum('fifo_pnl_realized'), order_by=F('date_time').asc()))
            .all()
            .order_by("-date_time")
        )

        context_data["trade_list"] = trade_list

        return context_data

grouping_detail_view = GroupingDetailView.as_view()
