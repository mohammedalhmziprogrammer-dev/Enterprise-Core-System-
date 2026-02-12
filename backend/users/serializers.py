
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.contrib.auth.models import *
from rest_framework.exceptions import ValidationError

from .models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
#user=get_user_model()
from activity_logs.signals import get_client_ip
from activity_logs.models import ActivityLog
from rest_framework.exceptions import AuthenticationFailed
from apps.baseserializer import BaseRulesSerializer
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class UserSerialzer(BaseRulesSerializer):
    
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
     
    roles = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    stractures = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    

    all_permissions = serializers.SerializerMethodField()
   
    class Meta:
        model = User
        fields = [
            'id','username', 'email', 'first_name', 'last_name', 
             'is_active', 'is_superuser',
            'must_change_password', 
            'administrative_structure_name', 'direct_manager',
            'direct_manager_name', 'data_visibility', 'data_visibility_display',
             'user_groups_count', 'all_permissions', 'roles', 'groups', 'stractures'
        ]
       #  fields='__all__'
        read_only_fields = ['date_joined', 'last_login']
        

   #  def get_permission_groups_count(self, obj):
   #      return obj.permissions_group.count()
   
    def get_user_groups_count(self, obj):
        return obj.groups.count()

    def get_all_permissions(self, obj):
         return obj.get_all_permissions()

    def get_roles(self, obj):
        return list(obj.groups.filter(role__isnull=False).values_list('id', flat=True))

    def get_groups(self, obj):
        return list(obj.groups.values_list('id', flat=True))



class UserCreateSerializer(BaseRulesSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone = serializers.CharField(
    required=False, 
    allow_null=True,  # ← أضف هذا
    allow_blank=True  # ← وهذا
    )
    # phone = serializers.CharField(
    #     # validators=[
    #     #     RegexValidator(
    #     #         regex=r'^7[0-9]{8}$',
    #     #         message=_('رقم الهاتف غير صحيح')
    #     #     )
    #     # ]
    # )
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
   
    
    class Meta:
        model = User
        # fields='__all__'
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone','must_change_password'
            
        ]

    def validate(self, attrs):
        if 'password' in attrs and not attrs['password']:
            raise serializers.ValidationError("Password is required.")
        return attrs
    
        
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        structures = validated_data.pop('stractures', [])
        groups = validated_data.pop('groups', [])
        
        # if not password:
        #     # Generate a strong random password
        #     import secrets
        #     import string
        #     alphabet = string.ascii_letters + string.digits + string.punctuation
        #     #password = ''.join(secrets.choice(alphabet) for i in range(12))
        #     #print(f"\n{'='*50}\nGENERATED PASSWORD FOR {validated_data.get('username')}: {password}\n{'='*50}\n")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.must_change_password = True
        user.save()
        
        # Store the generated password in the instance for the view to access if needed
       # user._generated_password = password
        
        return user
        
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
  def validate(self, attrs):
        request = self.context.get("request")

        try:
            # التوثيق الأساسي
            data = super().validate(attrs)
        
        except AuthenticationFailed:
           
            ActivityLog.objects.create(
                actor=attrs.get("user_id"),
                action_flag=ActivityLog.LOGIN_FAILED,
                app_label="auth",
                model_name="user",
                object_id=None,
                object_repr=attrs.get("username", ""),
                ip_address=get_client_ip(request) if request else None,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255] if request else None,
            )
            raise

        user = self.user

        ActivityLog.objects.create(
            actor=user,
            action_flag=ActivityLog.LOGIN,
            app_label="auth",
            model_name="user",
            object_id=str(user.pk),
            object_repr=str(user),
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255] if request else None,
        )

        # --- منطقك المخصص ---
        custom_user = User.objects.filter(username=user.username).first()

        if not custom_user:
            raise ValidationError("المستخدم غير موجود في النموذج المخصص")

        data["must_change_password"] = custom_user.must_change_password
        data["username"] = custom_user.username
        data["user_id"] = custom_user.id

        return data

  @classmethod
  def get_token(cls, user):
        token = super().get_token(user)

        custom_user = User.objects.filter(username=user.username).first()

        if custom_user:
            token["token_version"] = custom_user.token_version
            token["must_change_password"] = custom_user.must_change_password
            print(custom_user.must_change_password)
            token["username"] = custom_user.username
            token["user_id"] = custom_user.id 
            print( custom_user.id) # ← أضف هذا هنا


        return token

class UserUpdateSerializer(BaseRulesSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'stractures', 'direct_manager', 'data_visibility', 'is_active','must_change_password'

        ]
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)  # الآن إلزامي

    def validate(self, attrs):
        # جلب المستخدم من user_id المرسل
        try:
            user = User.objects.get(id=attrs['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("المستخدم غير موجود")

        # تحقق من كلمة المرور القديمة
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError("كلمة المرور القديمة غير صحيحة")

        # تحقق من التطابق
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("كلمات المرور غير متطابقة")

        attrs['user_instance'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user_instance']
        user.set_password(self.validated_data['new_password'])
        user.must_change_password = False
        user.save()
        return user

class RoleSerialzer(BaseRulesSerializer):
    class Meta:
        model=Role
        fields='__all__'        

class GroupSerialzer(BaseRulesSerializer):
    class Meta:
        model=Group
        fields='__all__' 
               

class PermissionsSerialzer(BaseRulesSerializer):
    content_type_app = serializers.CharField(source='content_type.app_label', read_only=True)
    content_type_model = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model=Permission
        fields=['id', 'name', 'codename', 'content_type', 'content_type_app', 'content_type_model']


