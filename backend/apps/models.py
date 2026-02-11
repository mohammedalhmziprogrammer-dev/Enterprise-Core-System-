
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now as DateTime
from codings.models import CodingCategory

#---------------------- App ------------------------------

#class BaseModel(models.Model):
    #created_at = models.DateTimeField(auto_now_add=True)
    ##updated_at = models.DateTimeField(auto_now=True)
    #is_active = models.BooleanField(default=True)
    #created_by=models.ForeignKey(User,models.PROTECT)
    #class Meta:
       # abstract = True

class AppType(models.Model):
    id = models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("App Type")
        verbose_name_plural = _("App Types")
        unique_together = [["id", "name"]]

    def __str__(self):
        return self.name

#------------------------------------------------------------------------------------------

class App(models.Model):
    app_label = models.CharField(primary_key=True,max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    appType = models.ForeignKey(AppType, on_delete=models.PROTECT, null=True, blank=True)
    app = models.ForeignKey('self', on_delete=models.PROTECT, null=True,related_name='app_parnet', blank=True, help_text=_("The parent app of this app, if any."),)
    url = models.CharField(max_length=200, null=True, blank=True)
    icon = models.FileField(upload_to='app_icons/', null=True, blank=True,default='app_icons/default_icon.png')
    order = models.IntegerField(auto_created=True,null=True, blank=True)
    codingCategory=models.ManyToManyField(CodingCategory, blank=True,related_name='app_codingcategory')
    is_menu = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
 

    
    class Meta:
        verbose_name = _("App")
        verbose_name_plural = _("Apps")
        unique_together = [["app_label", "appType"]]

    def __str__(self):
        return self.name

class AppVersion(models.Model):
    version = models.CharField(max_length=100)
    app = models.ForeignKey(App, on_delete=models.PROTECT, null=True, blank=True)
    appVersion = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True,help_text=_("The previous version of this app version, if any."),)    
    description = models.TextField(null=True, blank=True)
    path = models.FileField(upload_to='Versions/', null=True, blank=True,default='Versions/initialize.zip')
    
    release_date = models.DateTimeField(null=True, blank=True,default=DateTime)

    class Meta:
        verbose_name = _("App Version")
        verbose_name_plural = _("App Versions")
        unique_together = [["version", "app"]]

    def __str__(self):
        return f"{self.app } - V{self.version} {self.release_date}"    
#------------------------------------------------------------------------------------------

class Model(ContentType):
    class Meta:
        proxy = True
    @property
    def app(self):
        return App.objects.get(pk=self.app_label)
