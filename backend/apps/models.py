
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


#---------------------- App ------------------------------

class AppType(models.Model):
    id = models.CharField(primary_key=True,max_length=100,verbose_name=_('app type id'))
    name = models.CharField(max_length=100 ,verbose_name=_(" name type"))

    class Meta:
        verbose_name = _("app type")
        verbose_name_plural = _("app types")
        unique_together = [["id", "name"]]

    def __str__(self):
        return self.name

#------------------------------------------------------------------------------------------

class App(models.Model):
    app_label = models.CharField(primary_key=True,max_length=100 ,verbose_name=_(" App Label"))
    name = models.CharField(max_length=100, null=True, blank=True ,verbose_name=_("name app"))
    appType = models.ForeignKey(AppType, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_(" "))
    app = models.ForeignKey('self', on_delete=models.PROTECT, null=True,related_name='app_parnet', blank=True, help_text=_("The parent app of this app, if any."),verbose_name=_("Parent app"))
    url = models.CharField(max_length=200, null=True, blank=True ,verbose_name=_("App URL"))
    icon = models.FileField(upload_to='app_icons/', null=True, blank=True,default='app_icons/default_icon.png' ,verbose_name=_("App icon"))
    order = models.IntegerField(auto_created=True,null=True, blank=True ,verbose_name=_("Order"))
    codingCategory=models.ManyToManyField(CodingCategory, blank=True,related_name='app_codingcategory', verbose_name=_("Coding categories"))
    codings = models.ManyToManyField('codings.Coding', blank=True, related_name='app_codings', verbose_name=_("Codings"))
    is_core = models.BooleanField(default=False, verbose_name=_("Is Core App"), help_text=_("If true, this app is mandatory in all releases."))
    is_menu = models.BooleanField(default=False ,verbose_name=_("Menu"))
    description = models.TextField(null=True, blank=True ,verbose_name=_("Description"))
 

    
    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")
        unique_together = [["app_label", "appType"]]

    def __str__(self):
        return  self.name

class AppVersion(models.Model):
    version = models.CharField(max_length=100 ,verbose_name=_("App version"))
    app = models.ForeignKey(App, on_delete=models.PROTECT, null=True, blank=True ,verbose_name=_("Application"))
    appVersion = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True,help_text=_("The previous version of this app version, if any."), verbose_name=_("Previous version"))    
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    path = models.FileField(upload_to='Versions/', null=True, blank=True,default='Versions/initialize.zip' ,verbose_name=_("Release file"))
    
    release_date = models.DateTimeField(null=True, blank=True,default=DateTime , verbose_name=_("Release date"))

    class Meta:
        verbose_name = _("App version")
        verbose_name_plural = _("App versions")
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
