from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PortfoliosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finx_tracker.portfolios"
    verbose_name = _("Portfolios")
