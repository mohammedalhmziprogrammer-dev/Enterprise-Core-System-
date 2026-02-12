
from rest_framework import serializers
from .models import *
from apps.baseserializer import BaseRulesSerializer
from codings.serializers import CodingCategorySerializer
class AppTypeSerializer(BaseRulesSerializer):
    class Meta:
        model = AppType
        fields = '__all__'

 
class AppSerializer(BaseRulesSerializer):
    appType_name = serializers.CharField(source='appType.name', read_only=True)
    codingCategory_details = CodingCategorySerializer(source='codingCategory', many=True, read_only=True)
    
    class Meta:
        model = App
        fields = '__all__'

class AppVersionSerializer(BaseRulesSerializer):
    app_name = serializers.CharField(source='app.name', read_only=True)
    
    class Meta:
        model = AppVersion
        fields = '__all__'