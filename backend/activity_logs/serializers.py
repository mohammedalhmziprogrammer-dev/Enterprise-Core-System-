from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'actor', 'actor_name', 'action_time', 'action_flag',
            'app_label', 'model_name', 'object_repr', 'changes',
            'ip_address', 'user_agent'
        ]
