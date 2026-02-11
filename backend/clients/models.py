from django.db import models

from django.utils.translation import gettext_lazy as _
# Create your models here.
from django.contrib.auth.models import User

class Beneficiary(models.Model):
    public_name = models.CharField(max_length=100)
    pravite_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='images/', null=True, blank=True,default='images/default_image.png')
    order = models.IntegerField(auto_created=True,null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    right_address = models.TextField(null=True, blank=True)
    left_address = models.TextField(null=True, blank=True)
    class Meta:
        verbose_name = _("Beneficiary")
        verbose_name_plural = _("Beneficiary")

    def __str__(self):
        return self.public_name
    

class Level(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='sublvls', help_text=_("The parent level of this level, if any."),)
    count = models.IntegerField(null=True, blank=True, help_text=_("The number of structures at this level."),default=0)
    class Meta:
        verbose_name = _("Structure level")
        verbose_name_plural = _("Structure levels")

    def __str__(self):
        return self.name


class Structure(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    beneficiary = models.ManyToManyField(Beneficiary, blank=True,related_name='beneficiary_structure')
    level = models.ForeignKey(Level, on_delete=models.PROTECT, null=True, blank=True)
    structure = models.ForeignKey('self', on_delete=models.PROTECT,  related_name='children',null=True, blank=True, help_text=_("The parent structure of this structure, if any."),)
    image = models.FileField(upload_to='images/', null=True, blank=True,default='images/default_image.png')
    order = models.IntegerField(auto_created=True,null=True, blank=True)
    is_branch = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    right_address = models.TextField(null=True, blank=True)
    left_address = models.TextField(null=True, blank=True)
    

    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")

    def __str__(self):
        return self.name
