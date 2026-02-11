
from rest_framework import serializers
from django.contrib.auth.models import *

from .tests import check_phone_number 
from .models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
#user=get_user_model()

class UserSerialzer(serializers.ModelSerializer):
     administrative_structure_name = serializers.CharField(
         source='strcuter.name', 
         read_only=True
     )
     direct_manager_name = serializers.CharField(
         source='direct_manager.get_full_name', 
         read_only=True
     )
     data_visibility_display = serializers.CharField(
         source='get_data_visibility_display', 
         read_only=True
     )
     #permission_groups_count = serializers.SerializerMethodField()
     user_groups_count = serializers.SerializerMethodField()
    
     class Meta:
         model = User
         fields = [
             'id','username', 'email', 'first_name', 'last_name', 
              'is_active', 
             'must_change_password', 'administrative_structure', 
             'administrative_structure_name', 'direct_manager',
             'direct_manager_name', 'data_visibility', 'data_visibility_display',
              'user_groups_count'
         ]
        #  fields='__all__'
         read_only_fields = ['date_joined', 'last_login']
         

    #  def get_permission_groups_count(self, obj):
    #      return obj.permissions_group.count()
    
     def get_user_groups_count(self, obj):
         return obj.groups.count()
     class Meta:
        model=User
        fields= '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
   
    
    class Meta:
        model = User
        # fields='__all__'
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone'
            
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        structures = validated_data.pop('stractures', [])
        groups = validated_data.pop('groups', [])
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.must_change_password = True
        user.save()
        return user
        


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'stractures', 'direct_manager', 'data_visibility', 'is_active'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("كلمات المرور غير متطابقة")
        return attrs
class RoleSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Role
        fields='__all__'        

class GroupSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields='__all__' 
               

class PermissionsSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Permission
        fields='__all__'

