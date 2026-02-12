"""
Update Management Serializers
Handles serialization for update-related models.
"""
from rest_framework import serializers
from .update_models import Update, UpdateItem, ClientUpdate, UpdateLog
from .models import Release, ClientRelease
from apps.serializers import AppSerializer
from clients.serializers import BeneficiarySerializer
from users.serializers import UserSerialzer


class UpdateItemSerializer(serializers.ModelSerializer):
    """Serializer for UpdateItem model."""
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    change_type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    app_name = serializers.CharField(source='app.name', read_only=True)
    model_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = UpdateItem
        fields = [
            'id', 'update', 'item_type', 'item_type_display', 
            'app', 'app_name', 'content_type', 'model_name',
            'file_path', 'change_type', 'change_type_display',
            'description', 'order'
        ]
        read_only_fields = ['id']


class UpdateLogSerializer(serializers.ModelSerializer):
    """Serializer for UpdateLog model."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = UpdateLog
        fields = [
            'id', 'update', 'client_update', 'action', 'action_display',
            'performed_by', 'performed_by_name', 'performed_at',
            'details', 'ip_address'
        ]
        read_only_fields = ['id', 'performed_at']


class ClientUpdateSerializer(serializers.ModelSerializer):
    """Serializer for ClientUpdate model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    beneficiary_name = serializers.CharField(source='beneficiary.public_name', read_only=True)
    update_name = serializers.CharField(source='update.name', read_only=True)
    update_version = serializers.CharField(source='update.version', read_only=True)
    applied_by_name = serializers.CharField(source='applied_by.get_full_name', read_only=True)
    logs = UpdateLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = ClientUpdate
        fields = [
            'id', 'update', 'update_name', 'update_version',
            'client_release', 'beneficiary', 'beneficiary_name',
            'status', 'status_display', 'scheduled_at', 'started_at',
            'completed_at', 'applied_by', 'applied_by_name',
            'rollback_available', 'rollback_file', 'error_message',
            'notes', 'logs'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']


class ClientUpdateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing ClientUpdates."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    beneficiary_name = serializers.CharField(source='beneficiary.public_name', read_only=True)
    update_name = serializers.CharField(source='update.name', read_only=True)
    
    class Meta:
        model = ClientUpdate
        fields = [
            'id', 'update', 'update_name', 'beneficiary', 'beneficiary_name',
            'status', 'status_display', 'scheduled_at', 'completed_at'
        ]


class UpdateSerializer(serializers.ModelSerializer):
    """Full serializer for Update model."""
    update_type_display = serializers.CharField(source='get_update_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    base_release_name = serializers.CharField(source='base_release.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    items = UpdateItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    client_updates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Update
        fields = [
            'id', 'name', 'version', 'base_release', 'base_release_name',
            'update_type', 'update_type_display', 'status', 'status_display',
            'description', 'changelog', 'exported_file',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'requires_migration', 'is_mandatory', 'min_compatible_version',
            'items', 'items_count', 'client_updates_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'exported_file']
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_client_updates_count(self, obj):
        return obj.client_updates.count()


class UpdateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing Updates."""
    update_type_display = serializers.CharField(source='get_update_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    base_release_name = serializers.CharField(source='base_release.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    deployments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Update
        fields = [
            'id', 'name', 'version', 'base_release', 'base_release_name',
            'update_type', 'update_type_display', 'status', 'status_display',
            'created_at', 'is_mandatory', 'items_count', 'deployments_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_deployments_count(self, obj):
        return obj.client_updates.filter(status='completed').count()


class UpdateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Updates."""
    items = UpdateItemSerializer(many=True, required=False)
    
    class Meta:
        model = Update
        fields = [
            'name', 'version', 'base_release', 'update_type',
            'description', 'changelog', 'requires_migration',
            'is_mandatory', 'min_compatible_version', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        update = Update.objects.create(**validated_data)
        
        for item_data in items_data:
            UpdateItem.objects.create(update=update, **item_data)
        
        return update


class ApplyUpdateSerializer(serializers.Serializer):
    """Serializer for applying updates to clients."""
    beneficiary_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of beneficiary IDs to apply the update to."
    )
    scheduled_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Optional scheduled time for the update."
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for this deployment."
    )
