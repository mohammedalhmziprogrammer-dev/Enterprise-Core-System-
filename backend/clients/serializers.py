from apps.validation.validators import min_len, required, no_start_with_number
from .models import Beneficiary,Level, Structure
from rest_framework import serializers
from apps.baseserializer import BaseRulesSerializer

class BeneficiarySerializer(BaseRulesSerializer):
    image_url = serializers.SerializerMethodField()
    RULES = {
        "public_name": [(required,), (min_len, 3), (no_start_with_number,)]
    }
   

    #structures_count = serializers.SerializerMethodField()
    #image_url = serializers.SerializerMethodField()
    class Meta:
        model = Beneficiary
        fields = '__all__'
        #['public_name']
       # read_only_fields=['public_name']

    def get_structures_count(self, obj):
        return obj.beneficiary_structures.count()
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None 

    def update(self, instance, validated_data):
        # إذا لم يتم إرسال ملف جديد
        if 'image' not in validated_data or validated_data.get('image') is None:
            validated_data.pop('image', None)

        return super().update(instance, validated_data)       

        
class LevelSerializer(BaseRulesSerializer):
    RULES = {
        "name": [(required,), (min_len, 3), (no_start_with_number,)]
    }

    class Meta:
        model = Level
        fields = '__all__'
        

    def get_sublevels(self, obj):
        return LevelSerializer(obj.level, many=True).data
    

        
class StructureSerializer(BaseRulesSerializer):
    RULES = {
        "name": [(required,), (min_len, 3), (no_start_with_number,)]
    }
    
    parent_name = serializers.CharField(source='structure.name', read_only=True)
    #sub_structures = serializers.SerializerMethodField()
    #beneficiary= serializers.CharField()
    
    level_name = serializers.CharField(source='level.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def update(self, instance, validated_data):
        # إذا لم يتم إرسال ملف جديد
        if 'image' not in validated_data or validated_data.get('image') is None:
            validated_data.pop('image', None)

        return super().update(instance, validated_data)   

    class Meta:
        model = Structure
        fields = '__all__'
    
    def get_sub_structures(self, obj):
        return StructureSerializer(obj.sub_structures.all(), many=True).data
    
    # def get_beneficiary_names(self, obj):
    #     return [beneficiary.public_name for beneficiary in obj.beneficiary.all()]
   

        
# class StrcuterUsersSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField()
#     structures = serializers.StringRelatedField(many=True)

#     class Meta:
#         model = SupervisorStructure
#         fields = ['user', 'supervisor', 'structures']
#         def get_user_structures(self, obj):
#             return [structure.name for structure in obj.structures.all()]
        
#         def get_structure_users(self, obj):
#             return [user.get_full_name() for user in obj.users.all()]
        
#         def get_users_count(self, obj):
#          return obj.users.count()