from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TradesConfig(AppConfig):
    name = "finx_tracker.trades"
    verbose_name = _("Trades")
    default_auto_field = "django.db.models.BigAutoField"
