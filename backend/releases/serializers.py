
from rest_framework import serializers
from .models import Release, ReleaseBeneficiary, ReleaseGroup, ReleaseApp, ReleaseUser, ClientRelease
from apps.serializers import AppSerializer, AppVersionSerializer
from clients.serializers import BeneficiarySerializer
from users.serializers import GroupSerialzer, UserSerialzer
from apps.models import App

class ReleaseBeneficiarySerializer(serializers.ModelSerializer):
    beneficiary_details = BeneficiarySerializer(source='beneficiary', read_only=True)
    class Meta:
        model = ReleaseBeneficiary
        fields = ['id', 'release', 'beneficiary', 'beneficiary_details']

class ReleaseGroupSerializer(serializers.ModelSerializer):
    group_details = GroupSerialzer(source='group', read_only=True)
    class Meta:
        model = ReleaseGroup
        fields = ['id', 'release', 'group', 'group_details']

class ReleaseUserSerializer(serializers.ModelSerializer):
    user_details = UserSerialzer(source='user', read_only=True)
    class Meta:
        model = ReleaseUser
        fields = ['id', 'release', 'user', 'user_details']

class ReleaseAppSerializer(serializers.ModelSerializer):
    app_details = AppSerializer(source='app', read_only=True)
    version_details = AppVersionSerializer(source='version', read_only=True)
    class Meta:
        model = ReleaseApp
        fields = ['id', 'release', 'app', 'version', 'year', 'app_details', 'version_details', 'is_core']

class ClientReleaseSerializer(serializers.ModelSerializer):
    beneficiary_details = BeneficiarySerializer(source='beneficiary', read_only=True)
    class Meta:
        model = ClientRelease
        fields = ['id', 'release', 'beneficiary', 'beneficiary_details', 'is_active', 'active_from', 'active_to']

class ReleaseSerializer(serializers.ModelSerializer):
    beneficiaries = ReleaseBeneficiarySerializer(source='releasebeneficiary_set', many=True, read_only=True)
    assigned_clients = ClientReleaseSerializer(source='clientrelease_set', many=True, read_only=True)
    groups = ReleaseGroupSerializer(source='releasegroup_set', many=True, read_only=True)
    users = ReleaseUserSerializer(source='releaseuser_set', many=True, read_only=True)
    release_apps = ReleaseAppSerializer(source='releaseapp_set', many=True, read_only=True)
    
    # Write-only fields
    beneficiary_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    group_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    user_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    business_apps = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Release
        fields = [
            'id', 'name', 'descraption', 'version', 'base_release', 'is_update', 'release_date', 
            'status', 'exported_file', 
            'beneficiaries', 'assigned_clients', 'groups', 'users', 'release_apps', 
            'beneficiary_ids', 'group_ids', 'user_ids', 'business_apps',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        beneficiary_ids = validated_data.pop('beneficiary_ids', [])
        group_ids = validated_data.pop('group_ids', [])
        user_ids = validated_data.pop('user_ids', [])
        business_apps_labels = validated_data.pop('business_apps', [])
        
        from .services import ReleaseService
        
        # Use Service for creation (handles Core Apps, logic)
        release = ReleaseService.create_release(
            name=validated_data.get('name'),
            description=validated_data.get('descraption'),
            version=validated_data.get('version'),
            base_release=validated_data.get('base_release'),
            business_apps_labels=business_apps_labels
        )
        
        # Update other fields not handled by create_release if necessary
        for attr, value in validated_data.items():
            if hasattr(release, attr) and getattr(release, attr) != value:
                setattr(release, attr, value)
        release.save()

        # Handle other relations
        self._save_relations(release, beneficiary_ids, group_ids, user_ids)
        return release

    def update(self, instance, validated_data):
        beneficiary_ids = validated_data.pop('beneficiary_ids', None)
        group_ids = validated_data.pop('group_ids', None)
        user_ids = validated_data.pop('user_ids', None)
        business_apps_labels = validated_data.pop('business_apps', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update Apps
        if business_apps_labels is not None:
             # Remove non-core apps
             ReleaseApp.objects.filter(release=instance, is_core=False).delete()
             # Add new business apps
             from .services import ReleaseService
             # We can reuse the helper logic or manual add
             # Re-using internal logic from service is cleaner but it's private.
             # Let's duplicate logic for now or expose a helper in Service.
             # Service doesn't have public 'update_apps' method.
             
             core_apps_labels = ReleaseApp.objects.filter(release=instance, is_core=True).values_list('app__app_label', flat=True)
             
             new_apps = App.objects.filter(app_label__in=business_apps_labels).exclude(app_label__in=core_apps_labels)
             
             for app in new_apps:
                 ReleaseApp.objects.get_or_create(release=instance, app=app, defaults={'is_core': False})

        if beneficiary_ids is not None:
             instance.releasebeneficiary_set.all().delete()
             for bid in beneficiary_ids:
                ReleaseBeneficiary.objects.create(release=instance, beneficiary_id=bid)

        if group_ids is not None:
             instance.releasegroup_set.all().delete()
             for gid in group_ids:
                ReleaseGroup.objects.create(release=instance, group_id=gid)

        if user_ids is not None:
             instance.releaseuser_set.all().delete()
             for uid in user_ids:
                ReleaseUser.objects.create(release=instance, user_id=uid)

        return instance

    def _save_relations(self, release, beneficiary_ids, group_ids, user_ids):
        for bid in beneficiary_ids:
            ReleaseBeneficiary.objects.create(release=release, beneficiary_id=bid)
        
        for gid in group_ids:
            ReleaseGroup.objects.create(release=release, group_id=gid)
            
        for uid in user_ids:
            ReleaseUser.objects.create(release=release, user_id=uid)
