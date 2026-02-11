from django.db.models.signals import post_migrate
from django.apps import apps
from django.apps import apps as django_apps
from django.dispatch import receiver
from .models import App, AppVersion, AppType

@receiver(post_migrate)
def create_apps_after_migrate(sender, **kwargs):
    """
    Automatically create App records after migration.
    """
    try:
        # Skip for built-in apps that don’t have your model
        if not apps.is_installed('apps'):
            return
        from django.conf import settings
        for app_label in settings.INSTALLED_APPS:
            # Skip Django system apps
            if app_label.startswith('django.'):
                continue
            if app_label in getattr(settings, 'SYSTEM_APPS', []):
                continue
            # Create if not exists
            app_config = apps.app_configs[app_label]

            app = initialize_app(app_config.label, app_config.verbose_name )
            if '.' in app_label:
                parent_label = app_label.split('.')[0]
                parent_app_config = apps.app_configs[parent_label]
                parent_app = initialize_app(parent_app_config.label, parent_app_config.verbose_name )
                App.objects.update_or_create(
                    app_label=app_config.label,
                    defaults={'app': parent_app}
                )
    except Exception as e:
        print(f" App creation: {e}")

@receiver(post_migrate)
def remove_uninstalled_apps(sender, **kwargs):
    installed_labels = {app_config.label for app_config in django_apps.get_app_configs()}
    App.objects.exclude(app_label__in=installed_labels).delete()
    #print(f"App Delete done. ({installed_labels})")

def initialize_app(app_label,app_name,app_type="Fundamental"):
    appType,chkType = AppType.objects.get_or_create(name=app_type, defaults={'id':app_type} )
    if chkType:
        appType.save()
    app,chk = App.objects.get_or_create(app_label=app_label, defaults={'appType':appType,'url':f"/{app_label}", 'name':app_name or app_label.split('.')[-1].capitalize() , 'is_menu': False})
    if chk:
        app.save()
    appVersion,chkVersion = AppVersion.objects.get_or_create(app=app, version="1.0.0", defaults={'description':f"Initial version of {app.name}"})
    if chkVersion:
        appVersion.save()
    if chk:print(f"App initialization done. ({app_label})")
    return app            
    
    
        