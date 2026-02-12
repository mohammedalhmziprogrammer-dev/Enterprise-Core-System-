# core/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from activity_logs.middleware import get_current_user
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class BaseModel(models.Model):
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,verbose_name=_("Created by"),
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Updated by"),
        related_name="%(class)s_updated"
    )
    created_at = models.DateTimeField(default=timezone.now ,verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True ,verbose_name=_("Updated at"))
    is_active = models.BooleanField(default=True ,verbose_name=_("Active"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        # If creating for first time
        if not self.pk:
            if user and user.is_authenticated:
                self.created_by = user

        # Always update updated_by
        if user and user.is_authenticated:
            self.updated_by = user

        super().save(*args, **kwargs)
