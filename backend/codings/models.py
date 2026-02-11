from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CodingCategory(models.Model):
    CATEGORY_TYPES = [
        ('normal', _('عادي')),
        ('tree', _('شجرة')),
    ]
    
    general_name = models.CharField(_("الاسم العام"), max_length=200)
    specific_name = models.CharField(_("الاسم الخاص"), max_length=200, unique=True)
    type = models.CharField(
        _("النوع"),
        max_length=10,
        choices=CATEGORY_TYPES,
        default='normal'
    )
    CodingCategory = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("معتمد على فئة")
    )
    description = models.TextField(_("الوصف"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("فئة رموز")
        verbose_name_plural = _("فئات الرموز")
    
    def __str__(self):
        return self.general_name

class Coding(models.Model):
    name = models.CharField(_("الاسم"), max_length=200)
    coding = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True
        ,related_name='coding_parnet',
        verbose_name=_("الرمز الأب")
    )
    codingCategory = models.ForeignKey(
        CodingCategory,
        on_delete=models.PROTECT,
    
        verbose_name=_("الفئة")
    )

    category=models.CharField(max_length=100)
    order = models.IntegerField(_("الترتيب"), default=0)
    is_active=models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("رمز")
        verbose_name_plural = _("الرموز")
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name