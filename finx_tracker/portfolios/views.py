from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from finx_tracker.portfolios.aggregate_queries import agg_query_strategy_pnl
from finx_tracker.portfolios.models import Portfolio


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
