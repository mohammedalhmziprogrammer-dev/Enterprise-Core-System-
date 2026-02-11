from rest_framework import serializers
from .models import CodingCategory, Coding

class CodingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingCategory
        fields = '__all__'

class CodingSerializer(serializers.ModelSerializer):
    codingCategory_details = CodingCategorySerializer(source='codingCategory', read_only=True)
    
    class Meta:
        model = Coding
        fields = '__all__'
