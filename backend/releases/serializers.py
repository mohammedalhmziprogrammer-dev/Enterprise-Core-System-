from rest_framework import serializers
from .models import Release
from apps.serializers import AppSerializer
from clients.serializers import BeneficiarySerializer
from users.serializers import GroupSerialzer

class ReleaseSerializer(serializers.ModelSerializer):
    # Nested serializers for read operations to show details
    apps_details = AppSerializer(source='apps', many=True, read_only=True)
    beneficiary_details = BeneficiarySerializer(source='beneficiary', many=True, read_only=True)
    groups_details = GroupSerialzer(source='groups', many=True, read_only=True)

    class Meta:
        model = Release
        fields = '__all__'
