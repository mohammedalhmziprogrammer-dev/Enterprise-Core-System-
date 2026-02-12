
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
