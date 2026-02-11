from rest_framework import serializers
from .models import *

class AppTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppType
        fields = '__all__'

        
# class ModelSerializer(serializers.ModelSerializer):

#     class Meta:
#         model=Model
#         fields='__all__'
class AppSerializer(serializers.ModelSerializer):
    appType_name = serializers.CharField(source='appType.name', read_only=True)
    
    class Meta:
        model = App
        fields = '__all__'

class AppVersionSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source='app.name', read_only=True)
    
    class Meta:
        model = AppVersion
        fields = '__all__'