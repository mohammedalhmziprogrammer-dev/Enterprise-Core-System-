from django.db import models

from django.utils.translation import gettext_lazy as _
# Create your models here.
from django.contrib.auth.models import User

from apps.basemodel import BaseModel
# class BaseModel(models.Model):
#     create_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_created_by")
#     update_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_updated_by")
#     created_at = models.DateTimeField(auto_now_add=True)    
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)


#     class Meta:
#         abstract = True
        
class Beneficiary(BaseModel):
    public_name = models.CharField(max_length=100, verbose_name=_("Public name"))
    pravite_name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Private name"))
    image = models.FileField(upload_to='images/', null=True, blank=True,default='images/default_image.png' ,verbose_name=_("Logo"))
    order = models.IntegerField(auto_created=True,null=True, blank=True ,verbose_name=_("Order"))

    description = models.TextField(null=True, blank=True ,verbose_name=_("Description"))
    right_address = models.TextField(null=True, blank=True ,verbose_name=_("Right header"))
    left_address = models.TextField(null=True, blank=True, verbose_name=_("Left header"))
    class Meta:
        verbose_name = _("Beneficiary")
        verbose_name_plural = _("Beneficiaries")

    def __str__(self):
        return self.public_name
    

class Level(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Level name"))
    level = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='sublvls', help_text=_("The parent level of this level, if any."), verbose_name=_("Parent level"))
    count = models.IntegerField(null=True, blank=True, help_text=_("The number of structures at this level."),default=0, verbose_name=_("Number of levels"))
    class Meta:
        verbose_name = _("Structure level")
        verbose_name_plural = _("Structure levels")

    def __str__(self):
        return self.name


class Structure(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Structure name"))
    beneficiary = models.ForeignKey(Beneficiary, blank=True,null=True,related_name='beneficiary_structure', on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.PROTECT, null=True, blank=True, verbose_name=_("Level"))
    structure = models.ForeignKey('self', on_delete=models.PROTECT,  related_name='children',null=True, blank=True, help_text=_("The parent structure of this structure, if any."),verbose_name=_("Parent structure"))
    image = models.FileField(upload_to='images/', null=True, blank=True,default='images/default_image.png' ,verbose_name=_("Logo"))
    order = models.IntegerField(auto_created=True,null=True, blank=True ,verbose_name=_("Order"))
    is_branch = models.BooleanField(default=False ,verbose_name=_("Branch"))
    description = models.TextField(null=True, blank=True ,verbose_name=_("Description"))
    right_address = models.TextField(null=True, blank=True, verbose_name=_("Right header"))
    left_address = models.TextField(null=True, blank=True, verbose_name=_("Left header"))


    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")

    def __str__(self):
        return self.name
