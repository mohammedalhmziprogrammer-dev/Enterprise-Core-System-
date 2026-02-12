from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.basemodel import BaseModel
# Create your models here.

class CodingCategory(BaseModel):
    CATEGORY_TYPES = [
        ('normal', _('عادي')),
        ('tree', _('شجرة')),
    ]
    
    general_name = models.CharField(_("General name"), max_length=200)
    specific_name = models.CharField(_("Specific name"), max_length=200, unique=True)
    type = models.CharField(
        _("Type"),
        max_length=10,
        choices=CATEGORY_TYPES,
        default='normal'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent category")
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Coding category")
        verbose_name_plural = _("Coding categories")
    
    def __str__(self):
        return self.general_name

class Coding(BaseModel):
    name = models.CharField(_("Name"), max_length=200)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent code")
    )
    codingCategory = models.ForeignKey(
        CodingCategory,
        on_delete=models.PROTECT,
    
        verbose_name=_("Category")
    )

    category=models.CharField(max_length=100)
    # New field for symbol/code (e.g., 'YE' for Yemen, 'SA' for Sana'a)
    code = models.CharField(_("Symbol/Code"), max_length=50, blank=True, null=True)
    
    order = models.IntegerField(_("Order"), default=0)
  
    
    class Meta:
        verbose_name = _("Code")
        verbose_name_plural = _("Codes")
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

    def clean(self):
        # Cycle detection
        if self.parent:
            p = self.parent
            while p:
                if p == self:
                    raise ValidationError(_("لا يمكن أن يكون الرمز أبًا لنفسه (حلقة دائرية)."))
                p = p.parent

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_descendants(self):
        """
        Returns a set of all descendants. 
        Note: This is recursive and hits DB multiple times unless optimized or using CTE.
        For simple depth, this is acceptable.
        """
        descendants = set()
        children = self.children.all()
        for child in children:
            descendants.add(child)
            descendants.update(child.get_descendants())
        return descendants

    def get_ancestors(self):
        """Returns a list of ancestors ordered from immediate parent to root."""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors
        
    @property
    def level(self):
        return len(self.get_ancestors())