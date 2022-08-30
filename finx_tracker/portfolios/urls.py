from django.urls import path

from finx_tracker.portfolios.views import (
    portfolio_detail_view,
    portfolio_list_view,
    portfolio_pnl_view
)

app_name = "portfolios"

urlpatterns = [
    path("", view=portfolio_list_view, name="portfolios-list"),
    path("pnl", view=portfolio_pnl_view, name="portfolios-pnl"),
    path("<int:portfolio_id>/", view=portfolio_detail_view, name="detail"),
]
