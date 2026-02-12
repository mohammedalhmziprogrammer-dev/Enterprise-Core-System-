"""
Update Management Models
Handles tracking and management of incremental updates for the Release System.
"""
from django.db import models
from django.utils.timezone import now as DateTime
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from apps.models import App
from apps.basemodel import BaseModel
from clients.models import Beneficiary

User = get_user_model()


class Update(BaseModel):
    """
    Represents an update package that can be applied to client releases.
    """
    UPDATE_TYPE_CHOICES = (
        ('bugfix', _('Bug Fix')),
        ('improvement', _('Improvement')),
        ('feature', _('New Feature')),
        ('security', _('Security Patch')),
        ('hotfix', _('Hotfix')),
    )
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('testing', _('Testing')),
        ('ready', _('Ready for Deployment')),
        ('deployed', _('Deployed')),
        ('deprecated', _('Deprecated')),
    )
    
    name = models.CharField(max_length=200, verbose_name=_("Update Name"))
    version = models.CharField(max_length=50, verbose_name=_("Update Version"))
    base_release = models.ForeignKey(
        'Release', 
        on_delete=models.CASCADE, 
        related_name='updates',
        verbose_name=_("Base Release"),
        help_text=_("The release this update is based on.")
    )
    update_type = models.CharField(
        max_length=20, 
        choices=UPDATE_TYPE_CHOICES, 
        default='improvement',
        verbose_name=_("Update Type")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name=_("Status")
    )
    description = models.TextField(
        null=True, 
        blank=True, 
        verbose_name=_("Description")
    )
    changelog = models.TextField(
        null=True, 
        blank=True, 
        verbose_name=_("Changelog"),
        help_text=_("Markdown formatted changelog.")
    )
    exported_file = models.FileField(
        upload_to='update_exports/', 
        null=True, 
        blank=True, 
        verbose_name=_("Exported File")
    )
    requires_migration = models.BooleanField(
        default=False, 
        verbose_name=_("Requires Migration"),
        help_text=_("Whether this update includes database migrations.")
    )
    is_mandatory = models.BooleanField(
        default=False, 
        verbose_name=_("Mandatory Update"),
        help_text=_("If true, clients must apply this update.")
    )
    min_compatible_version = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name=_("Minimum Compatible Version"),
        help_text=_("Minimum client version required for this update.")
    )
    
    class Meta:
        verbose_name = _("Update")
        verbose_name_plural = _("Updates")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class UpdateItem(models.Model):
    """
    Represents an individual change within an update.
    """
    ITEM_TYPE_CHOICES = (
        ('app', _('Application')),
        ('model', _('Model')),
        ('service', _('Service')),
        ('view', _('View/API')),
        ('template', _('Template/UI')),
        ('setting', _('Configuration')),
        ('migration', _('Database Migration')),
        ('static', _('Static File')),
        ('translation', _('Translation')),
    )
    
    CHANGE_TYPE_CHOICES = (
        ('added', _('Added')),
        ('modified', _('Modified')),
        ('deleted', _('Deleted')),
        ('fixed', _('Fixed')),
    )
    
    update = models.ForeignKey(
        Update, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_("Update")
    )
    item_type = models.CharField(
        max_length=20, 
        choices=ITEM_TYPE_CHOICES,
        verbose_name=_("Item Type")
    )
    app = models.ForeignKey(
        App, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Application"),
        help_text=_("The application this change belongs to.")
    )
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Model"),
        help_text=_("For model-type changes.")
    )
    file_path = models.CharField(
        max_length=500, 
        null=True, 
        blank=True,
        verbose_name=_("File Path"),
        help_text=_("Relative path to the affected file.")
    )
    change_type = models.CharField(
        max_length=20, 
        choices=CHANGE_TYPE_CHOICES,
        verbose_name=_("Change Type")
    )
    description = models.TextField(
        null=True, 
        blank=True,
        verbose_name=_("Description")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order of application for this change.")
    )
    
    class Meta:
        verbose_name = _("Update Item")
        verbose_name_plural = _("Update Items")
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.get_item_type_display()}: {self.get_change_type_display()}"


class ClientUpdate(models.Model):
    """
    Tracks the deployment of an update to a specific client/beneficiary.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('downloading', _('Downloading')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('rolled_back', _('Rolled Back')),
        ('skipped', _('Skipped')),
    )
    
    update = models.ForeignKey(
        Update, 
        on_delete=models.CASCADE, 
        related_name='client_updates',
        verbose_name=_("Update")
    )
    client_release = models.ForeignKey(
        'ClientRelease', 
        on_delete=models.CASCADE, 
        related_name='applied_updates',
        verbose_name=_("Client Release")
    )
    beneficiary = models.ForeignKey(
        Beneficiary, 
        on_delete=models.CASCADE, 
        related_name='received_updates',
        verbose_name=_("Beneficiary")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_("Status")
    )
    scheduled_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Scheduled At")
    )
    started_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Started At")
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Completed At")
    )
    applied_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='applied_updates',
        verbose_name=_("Applied By")
    )
    rollback_available = models.BooleanField(
        default=True,
        verbose_name=_("Rollback Available")
    )
    rollback_file = models.FileField(
        upload_to='update_rollbacks/', 
        null=True, 
        blank=True,
        verbose_name=_("Rollback File"),
        help_text=_("Backup for rollback purposes.")
    )
    error_message = models.TextField(
        null=True, 
        blank=True,
        verbose_name=_("Error Message")
    )
    notes = models.TextField(
        null=True, 
        blank=True,
        verbose_name=_("Notes")
    )
    
    class Meta:
        verbose_name = _("Client Update")
        verbose_name_plural = _("Client Updates")
        unique_together = [['update', 'client_release']]
        ordering = ['-scheduled_at', '-id']
    
    def __str__(self):
        return f"{self.beneficiary.public_name} - {self.update.name}"


class UpdateLog(models.Model):
    """
    Audit log for update operations.
    """
    ACTION_CHOICES = (
        ('created', _('Created')),
        ('modified', _('Modified')),
        ('exported', _('Exported')),
        ('applied', _('Applied')),
        ('started', _('Started')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('rolled_back', _('Rolled Back')),
        ('cancelled', _('Cancelled')),
    )
    
    update = models.ForeignKey(
        Update, 
        on_delete=models.CASCADE, 
        related_name='logs',
        verbose_name=_("Update")
    )
    client_update = models.ForeignKey(
        ClientUpdate, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='logs',
        verbose_name=_("Client Update")
    )
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        verbose_name=_("Action")
    )
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Performed By")
    )
    performed_at = models.DateTimeField(
        default=DateTime,
        verbose_name=_("Performed At")
    )
    details = models.JSONField(
        null=True, 
        blank=True,
        verbose_name=_("Details"),
        help_text=_("Additional details in JSON format.")
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name=_("IP Address")
    )
    
    class Meta:
        verbose_name = _("Update Log")
        verbose_name_plural = _("Update Logs")
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.update.name} - {self.get_action_display()}"
