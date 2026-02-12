
from rest_framework import serializers
from .models import CodingCategory, Coding
from apps.baseserializer import BaseRulesSerializer

class CodingCategorySerializer(BaseRulesSerializer):
    class Meta:
        model = CodingCategory
        fields = '__all__'

class CodingSerializer(BaseRulesSerializer):
    codingCategory_details = CodingCategorySerializer(source='codingCategory', read_only=True)
    has_children = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    parent_name = serializers.ReadOnlyField(source='parent.name')
    
    class Meta:
        model = Coding
        fields = '__all__'
        
    def get_has_children(self, obj):
        return obj.children.exists()

class CodingTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for full tree structure (recursive).
    Be careful with depth.
    """
    children = serializers.SerializerMethodField()
    key = serializers.CharField(source='id')
    title = serializers.CharField(source='name')

    class Meta:
        model = Coding
        fields = ['key', 'title', 'id', 'name', 'code', 'children', 'is_active', 'order', 'parent']
        
    def get_children(self, obj):
        children = obj.children.all().order_by('order', 'name')
        return CodingTreeSerializer(children, many=True).data
