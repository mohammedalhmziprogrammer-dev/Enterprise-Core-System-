from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import  User, Permission,Role

# csrf_protect_m = method_decorator(csrf_protect)
# sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass



