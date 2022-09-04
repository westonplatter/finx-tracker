from django.urls import path

from finx_tracker.portfolios.views import (
    grouping_detail_view,
    portfolio_detail_view,
    portfolio_list_view,
    portfolio_pnl_view,
    trade_list_view,
    trade_update_view,
)

app_name = "portfolios"

urlpatterns = [
    path("", view=portfolio_list_view, name="portfolios-list"),
    path("pnl", view=portfolio_pnl_view, name="portfolios-pnl"),
    path("<int:portfolio_id>/", view=portfolio_detail_view, name="portfolio-detail"),
    path("trades/", view=trade_list_view, name="trades-list"),
    path("trades/<int:trade_id>", view=trade_update_view, name="trade-update"),
    path("groupings/<int:pk>/", view=grouping_detail_view, name="grouping-detail"),
]
