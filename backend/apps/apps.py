from django.apps import AppConfig
#from django.contrib.contenttypes.apps import ContentTypesConfig

class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'
    label = 'apps'
    verbose_name = "Apps"

    def ready(self):
        import apps.signals  # noqa