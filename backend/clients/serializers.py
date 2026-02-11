from .models import Beneficiary,Level, Structure
from rest_framework import serializers

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'
        #['public_name']
       # read_only_fields=['public_name']

    def get_structures_count(self, obj):
        return obj.beneficiary_structures.count()

        
class LevelSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = Level
        fields = '__all__'
        

    def get_sublevels(self, obj):
        return LevelSerializer(obj.level, many=True).data
    

        
class StructureSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='structure.name', read_only=True)
    #sub_structures = serializers.SerializerMethodField()
    beneficiary= serializers.CharField()
    level_name = serializers.CharField(source='level.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
   # parent_structure_name = serializers.CharField(source='structure.name', read_only=True)
    class Meta:
        model = Structure
        # fields=['']
        fields = ['name','left_address','right_address','beneficiary_name']
    
    def get_sub_structures(self, obj):
        return StructureSerializer(obj.sub_structures.all(), many=True).data
    
    def get_beneficiary_names(self, obj):
        return [beneficiary.public_name for beneficiary in obj.beneficiary.all()]
    #def get_user_names(self, obj):
       # return [user.username for beneficiary in obj.user.all()]
    class Meta:
        model=Structure
        fields='__all__'
   

        
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