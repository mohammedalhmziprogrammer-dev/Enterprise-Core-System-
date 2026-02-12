from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL

class ActivityLog(models.Model):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    LOGIN = 'login'
    LOGOUT = 'logout'
    LOGIN_FAILED = 'login_failed'
    FORCE_LOGOUT = 'force_logout'
    
    ACTION_CHOICES = (
        (CREATE, _('انشاء')),
        (UPDATE, _('تحديث')),
        (DELETE, _('حذف')),
        (LOGIN, _('تسجيل الدخول')),
        (LOGOUT, _('تسجيل الخروج')),
        (LOGIN_FAILED, _('فشل تسجيل الدخول')),
        (FORCE_LOGOUT, _('تسجيل الخروج القسري')),
    )

    actor = models.ForeignKey(
       User,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
        null=True,
        blank=True,
        verbose_name=_('Actor'),
    )
    action_time = models.DateTimeField(
        _('Action time'),
        default=now,
        editable=False,
        
    )
    action_flag = models.CharField(
        _('Action type'),
        max_length=32,
        choices=ACTION_CHOICES,
        
    )
    app_label = models.CharField(
    
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('App name'),
    )
    model_name = models.CharField(
      
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Screen name'),
    )
    object_id = models.CharField(
      
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Object ID'),
    )
    object_repr = models.CharField(
        
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Object representation'),
    )
    changes = models.JSONField(
       
        null=True,
        blank=True,
        verbose_name=_('Changes'),
    )
    ip_address = models.GenericIPAddressField(
      
        null=True,
        blank=True,
        verbose_name=_('IP address'),
    )
    user_agent = models.TextField(
      
        null=True,
        blank=True,
        verbose_name=_('User agent'),
    )
    
    class Meta:
        verbose_name = _('Activity log')
        verbose_name_plural = _('Activity logs')
        ordering = ('-action_time',)

    def __str__(self):
        return f'{self.actor} {self.action_flag} {self.object_repr}'
