from django.apps import AppConfig
from django.conf import settings


class ReceiptsConfig(AppConfig):
    default_auto_field = settings.DEFAULT_AUTO_FIELD
    name = 'apps.receipts'
