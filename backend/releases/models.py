from django.db import models
from django.utils.timezone import now as DateTime

from django.utils.translation import gettext_lazy as _
from apps.models import App
from clients.models import Beneficiary
from users.models import Group, User
from apps.models import App, AppVersion
from apps.basemodel import BaseModel
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Release(BaseModel):
    name=models.CharField(max_length=200,verbose_name=_("Release name"))
    descraption=models.TextField(null=True,blank=True ,verbose_name=_("Description"))
    is_update=models.BooleanField(default=False ,verbose_name=_("Update"))
    release_date=models.DateTimeField(default=DateTime ,verbose_name=_("Release date"))
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("Status"))
    exported_file = models.FileField(upload_to='release_exports/', null=True, blank=True, verbose_name=_("Exported File"))
    version = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Version"))
    base_release = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Base Release"), help_text=_("The release this was cloned from."))
    apps = models.ManyToManyField(App, blank=True, related_name='apps_release', through='ReleaseApp')
    
    class Meta:
        verbose_name = _("Releases")
        verbose_name_plural = _("Releases")
    
    def __str__(self):
        return self.name
    
class ReleaseBeneficiary(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"))
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, verbose_name=_("Beneficiary"))
    
    class Meta:
        verbose_name = _("Release Beneficiary")
        verbose_name_plural = _("Release Beneficiaries")
        unique_together = [["release", "beneficiary"]]
    
    def __str__(self):
        return f"{self.release.name} - {self.beneficiary.public_name}"
    
class ReleaseGroup(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_("Group"))
    
    class Meta:
        verbose_name = _("Release Group")
        verbose_name_plural = _("Release Groups")
        unique_together = [["release", "group"]]
    
    def __str__(self):

        return f"{self.release.name} - {self.group.name}"

class ReleaseUser(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    
    class Meta:
        verbose_name = _("Release User")
        verbose_name_plural = _("Release Users")
        unique_together = [["release", "user"]]
    
    def __str__(self):
        return f"{self.release.name} - {self.user.username}"
    
class ReleaseApp(models.Model): 
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"))
    year = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("Year"))
    version = models.ForeignKey(AppVersion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Version"))
    app = models.ForeignKey(App, on_delete=models.CASCADE, verbose_name=_("Application"))
    is_core = models.BooleanField(default=False, verbose_name=_("Is Core"), help_text=_("Inherited from App."))
    
    class Meta:
        verbose_name = _("Release Application")
        verbose_name_plural = _("Release Applications")
        unique_together = [["release", "app"]]
    
    def __str__(self):
        return f"{self.release.name} - {self.app.name}"

class ReleaseModel(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"), related_name='release_models')
    app = models.ForeignKey(App, on_delete=models.CASCADE, verbose_name=_("Application"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_("Model"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    can_create = models.BooleanField(default=True, verbose_name=_("Can Create"))
    can_read = models.BooleanField(default=True, verbose_name=_("Can Read"))
    can_update = models.BooleanField(default=True, verbose_name=_("Can Update"))
    can_delete = models.BooleanField(default=True, verbose_name=_("Can Delete"))

    class Meta:
        verbose_name = _("Release Model")
        verbose_name_plural = _("Release Models")
        unique_together = [["release", "content_type"]]

    def __str__(self):
        return f"{self.release.name} - {self.content_type.model}"

class ReleaseService(models.Model):
    release = models.ForeignKey(Release, on_delete=models.CASCADE, verbose_name=_("Release"), related_name='release_services')
    app = models.ForeignKey(App, on_delete=models.CASCADE, verbose_name=_("Application"))
    service_name = models.CharField(max_length=200, verbose_name=_("Service Name"))
    service_code = models.CharField(max_length=100, verbose_name=_("Service Code"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("Release Service")
        verbose_name_plural = _("Release Services")
        unique_together = [["release", "service_code"]]

    def __str__(self):
        return f"{self.release.name} - {self.service_name}"

class ClientRelease(models.Model):
    release = models.ForeignKey(Release, on_delete=models.PROTECT, verbose_name=_("Release"))
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, verbose_name=_("Beneficiary"), related_name='client_releases')
    is_active = models.BooleanField(default=False, verbose_name=_("Active"))
    active_from = models.DateTimeField(default=DateTime, verbose_name=_("Active From"))
    active_to = models.DateTimeField(null=True, blank=True, verbose_name=_("Active To"))

    class Meta:
        verbose_name = _("Client Release")
        verbose_name_plural = _("Client Releases")
    
    def __str__(self):
        return f"{self.beneficiary.public_name} - {self.release.name}"