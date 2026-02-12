from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ActivityLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity_logs'
    verbose_name = _('Activity Logs')

    def ready(self):
        import activity_logs.signals
