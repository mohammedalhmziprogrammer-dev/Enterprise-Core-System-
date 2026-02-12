"""
Update Management Services
Business logic for managing updates, exports, and deployments.
"""
import os
import json
import shutil
import tempfile
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction

from .update_models import Update, UpdateItem, ClientUpdate, UpdateLog
from .models import Release, ClientRelease
from clients.models import Beneficiary


class UpdateService:
    """
    Service class for managing updates.
    """
    
    @staticmethod
    @transaction.atomic
    def create_update(name, version, base_release_id, update_type='improvement', 
                      description=None, changelog=None, created_by=None, items=None):
        """
        Create a new update.
        
        Args:
            name: Update name
            version: Update version string
            base_release_id: ID of the base release
            update_type: Type of update (bugfix, improvement, feature, security, hotfix)
            description: Update description
            changelog: Markdown changelog
            created_by: User creating the update
            items: List of update items (dicts)
        
        Returns:
            Update instance
        """
        base_release = Release.objects.get(id=base_release_id)
        
        update = Update.objects.create(
            name=name,
            version=version,
            base_release=base_release,
            update_type=update_type,
            description=description,
            changelog=changelog,
            created_by=created_by,
            status='draft'
        )
        
        # Create update items if provided
        if items:
            for idx, item_data in enumerate(items):
                UpdateItem.objects.create(
                    update=update,
                    order=idx,
                    **item_data
                )
        
        # Log creation
        UpdateLog.objects.create(
            update=update,
            action='created',
            performed_by=created_by,
            details={'items_count': len(items) if items else 0}
        )
        
        return update
    
    @staticmethod
    def add_update_item(update_id, item_type, change_type, app_id=None, 
                        content_type_id=None, file_path=None, description=None):
        """
        Add an item to an existing update.
        """
        update = Update.objects.get(id=update_id)
        
        if update.status not in ['draft', 'testing']:
            raise ValueError("Cannot modify update after it's been deployed.")
        
        # Get next order number
        max_order = update.items.aggregate(models.Max('order'))['order__max'] or 0
        
        item = UpdateItem.objects.create(
            update=update,
            item_type=item_type,
            change_type=change_type,
            app_id=app_id,
            content_type_id=content_type_id,
            file_path=file_path,
            description=description,
            order=max_order + 1
        )
        
        return item
    
    @staticmethod
    def generate_update_package(update_id, user=None):
        """
        Generate an update package (ZIP) for deployment.
        
        This creates an incremental package containing only the changes.
        """
        update = Update.objects.get(id=update_id)
        
        # Generate manifest
        manifest = {
            'update': {
                'id': update.id,
                'name': update.name,
                'version': update.version,
                'type': update.update_type,
                'base_release': update.base_release.version,
                'requires_migration': update.requires_migration,
                'is_mandatory': update.is_mandatory,
                'min_compatible_version': update.min_compatible_version,
                'generated_at': str(timezone.now()),
            },
            'items': [],
            'changelog': update.changelog,
        }
        
        for item in update.items.all():
            manifest['items'].append({
                'type': item.item_type,
                'change': item.change_type,
                'app': item.app.app_label if item.app else None,
                'model': item.content_type.model if item.content_type else None,
                'file_path': item.file_path,
                'description': item.description,
                'order': item.order,
            })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            package_name = f"update_{update.version}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
            package_path = os.path.join(temp_dir, package_name)
            os.makedirs(package_path)
            
            # Write manifest
            manifest_path = os.path.join(package_path, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
            
            # Create changes directory (placeholder for actual file changes)
            changes_dir = os.path.join(package_path, 'changes')
            os.makedirs(changes_dir)
            
            # TODO: Copy actual changed files based on items
            # This would require integration with version control or file tracking
            
            # Create archive
            archive_path = shutil.make_archive(
                os.path.join(temp_dir, package_name),
                'zip',
                root_dir=temp_dir,
                base_dir=package_name
            )
            
            # Save to update
            with open(archive_path, 'rb') as f:
                update.exported_file.save(f"{package_name}.zip", ContentFile(f.read()))
            
            update.status = 'ready'
            update.save()
        
        # Log export
        UpdateLog.objects.create(
            update=update,
            action='exported',
            performed_by=user,
            details={'package_name': package_name}
        )
        
        return update.exported_file.url
    
    @staticmethod
    def validate_compatibility(update_id, beneficiary_id):
        """
        Check if an update is compatible with a beneficiary's current version.
        
        Returns:
            dict with 'compatible' (bool) and 'message' (str)
        """
        update = Update.objects.get(id=update_id)
        
        # Get client's current release
        try:
            client_release = ClientRelease.objects.get(
                beneficiary_id=beneficiary_id,
                is_active=True
            )
        except ClientRelease.DoesNotExist:
            return {
                'compatible': False,
                'message': 'No active release found for this beneficiary.'
            }
        
        # Check if update is for the same base release
        if client_release.release_id != update.base_release_id:
            # Check version compatibility
            if update.min_compatible_version:
                client_version = client_release.release.version
                if client_version < update.min_compatible_version:
                    return {
                        'compatible': False,
                        'message': f'Client version {client_version} is below minimum required ({update.min_compatible_version}).'
                    }
        
        # Check if update was already applied
        existing = ClientUpdate.objects.filter(
            update=update,
            client_release=client_release,
            status='completed'
        ).exists()
        
        if existing:
            return {
                'compatible': False,
                'message': 'This update has already been applied to this client.'
            }
        
        return {
            'compatible': True,
            'message': 'Update is compatible and can be applied.'
        }
    
    @staticmethod
    @transaction.atomic
    def apply_update(update_id, beneficiary_ids, user=None, scheduled_at=None, notes=None):
        """
        Apply an update to one or more beneficiaries.
        
        Args:
            update_id: ID of the update to apply
            beneficiary_ids: List of beneficiary IDs
            user: User performing the action
            scheduled_at: Optional scheduled time
            notes: Optional notes
        
        Returns:
            List of ClientUpdate instances created
        """
        update = Update.objects.get(id=update_id)
        
        if update.status not in ['ready', 'deployed']:
            raise ValueError("Update must be in 'ready' or 'deployed' status to apply.")
        
        client_updates = []
        
        for beneficiary_id in beneficiary_ids:
            # Get active client release
            try:
                client_release = ClientRelease.objects.get(
                    beneficiary_id=beneficiary_id,
                    is_active=True
                )
            except ClientRelease.DoesNotExist:
                continue
            
            # Check compatibility
            compat = UpdateService.validate_compatibility(update_id, beneficiary_id)
            if not compat['compatible']:
                continue
            
            # Get or create client update to avoid duplicate key error
            client_update, created = ClientUpdate.objects.get_or_create(
                update=update,
                client_release=client_release,
                defaults={
                    'beneficiary_id': beneficiary_id,
                    'status': 'pending' if scheduled_at else 'in_progress',
                    'scheduled_at': scheduled_at,
                    'started_at': None if scheduled_at else timezone.now(),
                    'applied_by': user,
                    'notes': notes
                }
            )
            
            if not created:
                # Already exists, skip
                continue
            
            # Log
            UpdateLog.objects.create(
                update=update,
                client_update=client_update,
                action='applied',
                performed_by=user,
                details={'beneficiary_id': beneficiary_id}
            )
            
            client_updates.append(client_update)
        
        # Update status
        if client_updates and update.status == 'ready':
            update.status = 'deployed'
            update.save()
        
        return client_updates
    
    @staticmethod
    def mark_update_completed(client_update_id, user=None):
        """Mark a client update as completed."""
        client_update = ClientUpdate.objects.get(id=client_update_id)
        client_update.status = 'completed'
        client_update.completed_at = timezone.now()
        client_update.save()
        
        UpdateLog.objects.create(
            update=client_update.update,
            client_update=client_update,
            action='completed',
            performed_by=user
        )
        
        return client_update
    
    @staticmethod
    def mark_update_failed(client_update_id, error_message, user=None):
        """Mark a client update as failed."""
        client_update = ClientUpdate.objects.get(id=client_update_id)
        client_update.status = 'failed'
        client_update.error_message = error_message
        client_update.save()
        
        UpdateLog.objects.create(
            update=client_update.update,
            client_update=client_update,
            action='failed',
            performed_by=user,
            details={'error': error_message}
        )
        
        return client_update
    
    @staticmethod
    @transaction.atomic
    def rollback_update(client_update_id, user=None):
        """
        Rollback a failed or completed update.
        """
        client_update = ClientUpdate.objects.get(id=client_update_id)
        
        if not client_update.rollback_available:
            raise ValueError("Rollback is not available for this update.")
        
        if client_update.status not in ['completed', 'failed', 'in_progress']:
            raise ValueError("Cannot rollback an update that hasn't been applied.")
        
        # Perform rollback logic here
        # This would restore from rollback_file if available
        
        client_update.status = 'rolled_back'
        client_update.rollback_available = False
        client_update.save()
        
        UpdateLog.objects.create(
            update=client_update.update,
            client_update=client_update,
            action='rolled_back',
            performed_by=user
        )
        
        return client_update
    
    @staticmethod
    def get_pending_updates_for_beneficiary(beneficiary_id):
        """
        Get all pending/available updates for a beneficiary.
        """
        try:
            client_release = ClientRelease.objects.get(
                beneficiary_id=beneficiary_id,
                is_active=True
            )
        except ClientRelease.DoesNotExist:
            return Update.objects.none()
        
        # Get already applied updates
        applied_update_ids = ClientUpdate.objects.filter(
            beneficiary_id=beneficiary_id,
            status__in=['completed', 'in_progress', 'pending']
        ).values_list('update_id', flat=True)
        
        # Get compatible updates
        return Update.objects.filter(
            base_release=client_release.release,
            status__in=['ready', 'deployed']
        ).exclude(id__in=applied_update_ids)
    
    @staticmethod
    def get_update_stats(update_id):
        """Get deployment statistics for an update."""
        update = Update.objects.get(id=update_id)
        
        client_updates = update.client_updates.all()
        
        return {
            'total_deployments': client_updates.count(),
            'pending': client_updates.filter(status='pending').count(),
            'in_progress': client_updates.filter(status='in_progress').count(),
            'completed': client_updates.filter(status='completed').count(),
            'failed': client_updates.filter(status='failed').count(),
            'rolled_back': client_updates.filter(status='rolled_back').count(),
        }
