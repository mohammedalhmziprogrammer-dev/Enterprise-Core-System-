from django.contrib.auth.models import Group as BaseGroup , Permission as BasePermission,User as BaseUser
from django.db import models
from django.db.models import Q
from codings.models import Coding,CodingCategory
from clients.models import Structure
from django.utils.translation import gettext_lazy as _

class Permission(BasePermission):
    class Meta:
        proxy = True

    

class Group(BaseGroup):
    class Meta:
        proxy = True


class Role(BaseGroup):
    group = models.ForeignKey(
        Group,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name='group_roles',
        help_text=_("The group roles of this group, if any."),
    )
    codingCategory=models.ManyToManyField(CodingCategory,blank=True)
    coding=models.ManyToManyField(Coding,blank=True)
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
    def __str__(self):
        return self.name
   
    
class User(BaseUser):
    stractures=models.ManyToManyField(
        Structure,
        blank=True,
        related_name='stractures_user',
        help_text=_("The stractures of this user belongs to."),
    )
    direct_manager = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("المسؤول المباشر")
    )
    data_visibility = models.CharField(
        _("صلاحيات رؤية البيانات"),
        max_length=10,
        choices=[
            ('self', _('بيانات المستخدم فقط')),
            ('department', _('بيانات الهيكل الإداري')),
            ('all', _('جميع البيانات في النظام')),
        ],
        default='self'
    )
    must_change_password = models.BooleanField(_("يجب تغيير كلمة المرور"), default=True)
    phone = models.CharField(verbose_name='رقم الجوال',max_length=32)


    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمين")
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    _roles = None
    @property
    def roles(self):
        return self.groups.filter(role__in=Role.objects.all())

    @roles.setter
    def roles(self, value):
        try:
            groups = hasattr(value,'role') and [value.role] or [role.role for role in value] 
            self.groups.add(*groups)
        except:
            self._roles = value
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._roles:
            groups = hasattr(self._roles,'role') and [self._roles.role] or [role.role for role in self._roles] 
            self.groups.add(*groups)
            self._roles = None
            self.save()
        roles = Role.objects.filter(group__isnull=False).exclude(group_ptr__in=self.groups.all())
        groups =  [group.role for group in roles.filter(~Q(group_ptr__in=self.groups.all()))]
        if groups:
           self.groups.add(*groups) 
        
