from django.urls import path

from finx_tracker.portfolios.views import (
    GroupingDetailView,
    PortfolioDetailView,
    PortfolioListView,
    PortfolioPnlView,
    TradeListView,
    TradeUpdateView,
)

app_name = "portfolios"

urlpatterns = [
    path("", view=PortfolioListView.as_view(), name="portfolios-list"),
    path("pnl", view=PortfolioPnlView.as_view(), name="portfolios-pnl"),
    path("<int:portfolio_id>/", view=PortfolioDetailView.as_view(), name="portfolio-detail"),
    path("trades/", view=TradeListView.as_view(), name="trades-list"),
    path("trades/<int:trade_id>", view=TradeUpdateView.as_view(), name="trade-update"),
    path("groupings/<int:pk>/", view=GroupingDetailView.as_view(), name="grouping-detail"),
]
