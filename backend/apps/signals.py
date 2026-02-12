from django.db.models.signals import post_migrate
from django.apps import apps
from django.apps import apps as django_apps
from django.dispatch import receiver
from .runtime import RuntimeState
from .models import App, AppVersion, AppType
from django.conf import settings
@receiver(post_migrate)
def create_apps_after_migrate(sender, **kwargs):
    if not django_apps.is_installed('apps'):
        return

    RuntimeState.disable_activity_logs = True  # 

    try:
        project_apps = getattr(settings, 'PROJECT_APPS', [])
        for app_label in project_apps:
            app_config = django_apps.get_app_config(app_label)
            initialize_app(
                app_label=app_config.label,
                app_name=app_config.verbose_name,
            )
    finally:
        RuntimeState.disable_activity_logs = False 

@receiver(post_migrate)
def remove_uninstalled_apps(sender, **kwargs):
    """
    Remove apps from DB that are no longer in PROJECT_APPS
    """
    project_apps = set(getattr(settings, 'PROJECT_APPS', []))
    App.objects.exclude(app_label__in=project_apps).delete()

def initialize_app(app_label, app_name, app_type="Fundamental"):
    """
    Initialize App, AppType and AppVersion safely
    """

    app_type_obj, _ = AppType.objects.get_or_create(
        id=app_type,
        name=app_type
    )    

    app, created = App.objects.get_or_create(
        app_label=app_label,
        defaults={
            'name': app_name or app_label.capitalize(),
            'appType': app_type_obj,
            'url': f'/{app_label}/',
            'is_menu': False,
        }
    )

    AppVersion.objects.get_or_create(
        app=app,
        version="1.0.0",
        defaults={
            'description': f'Initial version of {app.name}'
        }
    )

    if created:
        print(f'App initialized: {app_label}')

    return app  
from django.db.models.signals import m2m_changed
from codings.models import Coding

@receiver(m2m_changed, sender=App.codingCategory.through)
def sync_app_codings(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Automatically add/remove Codings to the App when CodingCategories are added/removed.
    """
    if action == "post_add":
        # Find all codings belonging to the added categories
        codings_to_add = Coding.objects.filter(codingCategory__id__in=pk_set)
        instance.codings.add(*codings_to_add)
    
    elif action == "post_remove":
        # Find all codings belonging to the removed categories
        codings_to_remove = Coding.objects.filter(codingCategory__id__in=pk_set)
        instance.codings.remove(*codings_to_remove)    
    
        