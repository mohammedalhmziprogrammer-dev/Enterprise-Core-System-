from django.db import models
from django.utils.timezone import now as DateTime

from django.utils.translation import gettext_lazy as _
from apps.models import App
from clients.models import Beneficiary
from users.models import Group
# Create your models here.
class Release(models.Model):
    name=models.CharField(max_length=200)
    descraption=models.TextField(null=True,blank=True)
    is_update=models.BooleanField(default=False)
    release_date=models.DateTimeField(default=DateTime)
    beneficiary = models.ManyToManyField(Beneficiary, blank=True,related_name='beneficiary_release')
    apps = models.ManyToManyField(App, blank=True,related_name='apps_release')
    groups = models.ManyToManyField(Group, blank=True,related_name='groups_release')
    
    class Meta:
        verbose_name = _("الاصدارات")
        verbose_name_plural = _("الاصدارات")
    
    def __str__(self):
        return self.name