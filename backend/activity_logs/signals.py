import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

from apps.runtime import RuntimeState
from .models import ActivityLog
from .middleware import get_current_request, get_current_user
from users.models import User as CustomUser
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

# List of models to ignore (optional)
IGNORE_MODELS = ['ActivityLog', 'Session', 'LogEntry']

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ in IGNORE_MODELS:
        return
    if RuntimeState.disable_activity_logs:
        return  

    request = get_current_request()
    user = get_current_user()

    print(user)
    # If no user is authenticated (e.g. system task) maybe we can skip or log as system
    # For now, let's log if we have a request or user, or just log everything?
    # User requirement: "The user who performed the action."
    
    if not request:
        # If outside request cycle (e.g. shell), we might still want to log, but actor is None
        pass

    action_flag = ActivityLog.CREATE if created else ActivityLog.UPDATE
    
    # Calculate changes
    changes = {}
    if not created:
        # TODO: To get old values, we need pre_save.
        # But commonly we just log 'New Values' for update if we didn't capture old.
        # TO DO PROPERLY: connect to pre_save as well to store old state on the instance
        pass
    
    # Simple approach for now based on post_save:
    # We can capture the full current state.
    # To get diffs, we ideally need to know what it was before.
    # Let's attach a 'pre_save' handler to stash the old instance.
    
    final_changes = getattr(instance, '_activity_log_changes', None)
    
    ActivityLog.objects.create(
        actor=user if user and user.is_authenticated else None,
        action_flag=action_flag,
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes=final_changes,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] if request else None
    )

from django.db.models.signals import pre_save
@receiver(pre_save)
def capture_old_state(sender, instance, **kwargs):
    if sender.__name__ in IGNORE_MODELS:
        return
    
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            old_dict = model_to_dict(old_instance)
            new_dict = model_to_dict(instance)
            
            changes = {}
            for key, value in new_dict.items():
                if key in old_dict and old_dict[key] != value:
                    # Convert to string or simplify for JSON
                    old_val = str(old_dict[key])
                    new_val = str(value)
                    changes[key] = {'old': old_val, 'new': new_val}
            
            instance._activity_log_changes = changes
        except sender.DoesNotExist:
            instance._activity_log_changes = None
    else:
        instance._activity_log_changes = None # New object

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ in IGNORE_MODELS:
        return

    request = get_current_request()
    user = get_current_user()

    ActivityLog.objects.create(
        actor=user if user and user.is_authenticated else None,
        action_flag=ActivityLog.DELETE,
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes=None, # Or maybe dump the object?
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] if request else None
    )
