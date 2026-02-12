
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .models import *
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, viewsets, status, permissions, filters
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType
# from api.base import UnifiedModelViewSet
from apps.baseview import BaseViewSet 
from api.codes import *
from api.utils import standard_response
from django_filters.rest_framework.backends import DjangoFilterBackend
from collections import defaultdict

# User ViewSet with comprehensive functionality
#

class UserViewSet(BaseViewSet):

    queryset = User.objects.all().select_related('direct_manager').prefetch_related('stractures', 'groups')
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication,SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'data_visibility', 'must_change_password']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined', 'last_login', 'first_name', 'last_name']
    ordering = ['-date_joined']
    created_code = USER_CREATED
    updated_code = USER_UPDATED
    deleted_code = USER_DELETED
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        # elif self.action == 'change_password':
        #     return ChangePasswordSerializer
        return UserSerialzer
    
    def get_queryset(self):
        # Call BaseViewSet's get_queryset first to apply visibility rules
        queryset = super().get_queryset()
        
        # Filter by structure
        structure_id = self.request.query_params.get('structure', None)
        if structure_id:
            queryset = queryset.filter(stractures__id=structure_id)
        
        # Filter by role
        role_id = self.request.query_params.get('role', None)
        if role_id:
            queryset = queryset.filter(groups__role__id=role_id)
        
        # Filter by group
        group_id = self.request.query_params.get('group', None)
        if group_id:
            queryset = queryset.filter(groups__id=group_id)
        
        return queryset.distinct()
    @action(detail=True, methods=['post'])    
    def freezing(self, request, pk=None):
        """تجميد أو إلغاء تجميد حساب المستخدم"""
        user = self.get_object()
        user.is_active = False if user.is_active else True
        user.save()
        code = USER_FROZEN if not user.is_active else USER_UNFROZEN
        return standard_response(code, {'is_active': user.is_active})

    @action(detail=False, methods=['get'])
    def me(self, request):
        """الحصول على بيانات المستخدم الحالي"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_permissions(self):
        """تخصيص الصلاحيات لكل إجراء"""
        if self.action == 'change_password':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        
        if not serializer.is_valid():
             return standard_response(VALIDATION_ERROR, serializer.errors, success=False, status_code=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return standard_response(PASSWORD_CHANGED, {
            'must_change_password': user.must_change_password,
            'user_id': user.id
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """إعادة تعيين كلمة مرور المستخدم"""
        user = self.get_object()
        new_password = request.data.get('new_password', 'password123')
        user.set_password(new_password)
        user.must_change_password = True
        user.save()
        return standard_response(PASSWORD_RESET, {'user_id': user.id})

    @action(detail=True, methods=['post'])
    def assign_groups(self, request, pk=None):
        """تعيين مجموعات للمستخدم"""
        user = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        # Get current groups that are Roles (preserve them)
        role_groups = user.groups.filter(role__isnull=False)
        
        # Get new groups
        new_groups = Group.objects.filter(id__in=group_ids)
        
        # Combine
        groups_to_set = list(role_groups) + list(new_groups)
        user.groups.set(groups_to_set)
        
        return standard_response(GROUPS_ASSIGNED, {
             'groups': GroupSerialzer(new_groups, many=True).data
        })
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """تعيين أدوار للمستخدم"""
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        # Get current groups that are NOT roles (preserve them)
        non_role_groups = user.groups.filter(role__isnull=True)
        
        # Get new roles
        new_roles = Role.objects.filter(id__in=role_ids)
        
        # Collect all groups to set: preserved groups + new roles + linked groups
        groups_to_set = list(non_role_groups) + list(new_roles)
        
        for role in new_roles:
            if role.group:
                groups_to_set.append(role.group)
        
        user.groups.set(groups_to_set)
        
        return standard_response(ROLES_ASSIGNED, {
            'roles': RoleSerialzer(new_roles, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """الحصول على صلاحيات المستخدم"""
        user = self.get_object()
        user_permissions = user.user_permissions.all()
        group_permissions = Permission.objects.filter(group__user=user)
        all_permissions = Permission.objects.filter(Q(user=user) | Q(group__user=user)).distinct()  
                                                              
   
        
        return Response({
            'user_permissions': PermissionsSerialzer(user_permissions, many=True).data,
            'group_permissions': PermissionsSerialzer(group_permissions, many=True).data,
            'all_permissions': PermissionsSerialzer(all_permissions, many=True).data
        })
    @action(detail=False, methods=['get'])
    def user_permissions(self, request):
        """الحصول على صلاحيات المستخدم"""
        user = self.request.user
        user_permission = user.get_all_permissions()
        print(user_permission) 
        app = defaultdict(lambda: defaultdict(list))
        for row in user_permission:
            items = row.split('.')
            app_label = items[0]
            sub_items = items[1].split('_')
            model_name = sub_items[1]
            permission_name = sub_items[0]
            if(app.get(app_label)):
                if(app[app_label].get(model_name)):
                    app[app_label][model_name].append(permission_name)
                else:app[app_label][model_name] = [permission_name]
            else:app[app_label] = {model_name:[permission_name]}
                                                
        return Response(
            app
        
        )
  
    @action(detail=False, methods=['get'])
    def user_per(self, request):
        user = request.user
        user_permissions = user.get_all_permissions()
        print(user_permissions) 
        res={}
        for row in user_permissions:
            items = row.split('.')
            app_label = items[0]
            sub_items = items[1].split('_')
            model_name = sub_items[1]
            permission_name = sub_items[0]
            if(res.get(app_label)):
                if(res[app_label].get(model_name)):
                    res[app_label][model_name].append(permission_name)
                else:res[app_label][model_name] = [permission_name]
            else:res[app_label] = {model_name:[permission_name]}


        
        
        

        return Response(res)
    
    @action(detail=True, methods=['post'])
    def assign_structures(self, request, pk=None):
        """تعيين هياكل إدارية للمستخدم"""
        user = self.get_object()
        structure_ids = request.data.get('structure_ids', [])
        
        from clients.models import Structure
        structures = Structure.objects.filter(id__in=structure_ids)
        user.stractures.set(structures)
        
        return standard_response(STRUCTURES_ASSIGNED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات المستخدمين"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        must_change_password = User.objects.filter(must_change_password=True).count()
        
        # Data visibility statistics
        visibility_stats = User.objects.values('data_visibility').annotate(count=Count('id'))
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'staff_users': staff_users,
            'superusers': superusers,
            'must_change_password': must_change_password,
            'visibility_stats': list(visibility_stats)
        })
    
    @action(detail=True, methods=['get'])
    def subordinates_list(self, request, pk=None):
        """قائمة المرؤوسين المباشرين"""
        user = self.get_object()
        subordinates = user.subordinates.all()
        return Response(UserSerialzer(subordinates, many=True).data)

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Role ViewSet with enhanced functionality
class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all().prefetch_related('permissions', 'codingCategory', 'coding')
    serializer_class = RoleSerialzer
    permission_classes = [permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    created_code = ROLE_CREATED
    updated_code = ROLE_UPDATED
    deleted_code = ROLE_DELETED
    frozen_code = ROLE_FROZEN
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """تعيين صلاحيات للدور"""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        
        return standard_response(PERMISSIONS_ASSIGNED, {
            'permissions': PermissionsSerialzer(permissions, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """الحصول على المستخدمين المعينين لهذا الدور"""
        role = self.get_object()
        if role.group:
            users = User.objects.filter(groups=role.group)
            return Response(UserSerialzer(users, many=True).data)
        return Response([])
    

    @action(detail=True, methods=['post'])
    def assign_coding_categories(self, request, pk=None):
        """
        تعيين فئات الترميز للدور
        + إضافة جميع الرموز التابعة لهذه الفئات
        """
        role = self.get_object()
        category_ids = request.data.get('category_ids', [])

        if not category_ids:
            return standard_response("NO_CATEGORIES_PROVIDED", status=400)

        # جلب الفئات
        categories = CodingCategory.objects.filter(id__in=category_ids)

        if not categories.exists():
            return standard_response("CATEGORIES_NOT_FOUND", status=404)

        # ✅ جلب الرموز التابعة للفئات (ForeignKey)
        codings = Coding.objects.filter(
            codingCategory__in=categories,
            is_active=True
        ).distinct()

        # ربط الفئات بالدور
        role.codingCategory.add(*categories)

        # ربط الرموز بالدور
        role.coding.add(*codings)

        return standard_response(CODING_CATEGORIES_ASSIGNED)
        
    @action(detail=True, methods=['post'])
    def assign_codings(self, request, pk=None):
        """تعيين رموز للدور"""
        role = self.get_object()
        coding_ids = request.data.get('coding_ids', [])
        
        from codings.models import Coding
        codings = Coding.objects.filter(id__in=coding_ids)
        role.coding.set(codings)
        
        return standard_response(CODINGS_ASSIGNED)


# Group ViewSet with enhanced functionality
class GroupViewSet(BaseViewSet):
    queryset = Group.objects.all().prefetch_related('permissions')
    serializer_class = GroupSerialzer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    created_code = GROUP_CREATED
    updated_code = GROUP_UPDATED
    deleted_code = GROUP_DELETED
    frozen_code = GROUP_FROZEN
    
    @action(detail=True, methods=['get'])
    def group_per(self, request, pk=None):
        """الحصول على صلاحيات المجموعة"""
        group = self.get_object()
        per = group.permissions.values_list('codename', flat=True)
        return Response({
            'group': group.name,
            'permission': list(per)
        })
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """تعيين صلاحيات للمجموعة"""
        group = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        group.permissions.set(permissions)
        
        return standard_response(PERMISSIONS_ASSIGNED, {
            'permissions': PermissionsSerialzer(permissions, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """الحصول على المستخدمين في هذه المجموعة"""
        group = self.get_object()
        users = User.objects.filter(groups=group)
        return Response(UserSerialzer(users, many=True).data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات المجموعات"""
        groups_with_users = Group.objects.annotate(user_count=Count('user')).values('id', 'name', 'user_count')
        return Response(list(groups_with_users))

from django.conf import settings
# Permission ViewSet with enhanced functionality
class PermissionsViewSet(BaseViewSet):
    queryset = Permission.objects.all().select_related('content_type')

    serializer_class = PermissionsSerialzer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type']
    search_fields = ['name', 'codename']
    ordering_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']
    created_code = PERMISSION_CREATED
    updated_code = PERMISSION_UPDATED
    deleted_code = PERMISSION_DELETED
    frozen_code = PERMISSION_FROZEN

    # @action(detail=False, methods=['get'])
    # def by_app(self, request):
    #     """
    #     تجميع الصلاحيات حسب التطبيق
    #     (لتطبيقات المشروع فقط)
    #     """

    #     project_apps = settings.PROJECT_APPS

    #     permissions = (
    #         Permission.objects
    #         .filter(content_type__app_label__in=project_apps)
    #         .select_related('content_type')
    #         .order_by('content_type__app_label', 'content_type__model')
    #     )

    #     grouped = {}

    #     for perm in permissions:
    #         app_label = perm.content_type.app_label

    #         grouped.setdefault(app_label, []).append(
    #             PermissionsSerialzer(perm).data
    #         )

    #     return Response(grouped)
    

    @action(detail=False,methods=['get'])
    def by_app(self,requset):
        app_pro=settings.PROJECT_APPS
        permission=(Permission.objects.filter(content_type__app_label__in=app_pro).select_related('content_type').order_by('content_type__app_label', 'content_type__model'))
        group={}
        for per in permission:
            app_label=per.content_type.app_label
            group.setdefault(app_label,[]).append(PermissionsSerialzer(per).data)

        return Response(group)    



    # @action(detail=False, methods=['get'])
    # def by_app(self, request):
    #     """تجميع الصلاحيات حسب التطبيق"""
    #     project_apps = settings.PROJECT_APPS
    #     permissions = Permission.objects.all().select_related('content_type')

    #     grouped = {}
        
    #     for perm in permissions:
    #         app_label = perm.content_type.app_label
    #         if app_label not in grouped:
    #             grouped[app_label] = []
    #         grouped[app_label].append(PermissionsSerialzer(perm).data)
        
    #     return Response(grouped)
    
    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """تجميع الصلاحيات حسب النموذج"""
        permissions = Permission.objects.all().select_related('content_type')
        grouped = {}
        
        for perm in permissions:
            model = perm.content_type.model
            if model not in grouped:
                grouped[model] = []
            grouped[model].append(PermissionsSerialzer(perm).data)
        
        return Response(grouped)  
    
    # @action(detail=False, methods=['get'])
    # def by_app(self, request):
  
    #     permissions = Permission.objects.select_related('content_type')

    #     grouped = {}

    #     for perm in permissions:
    #         app_label = perm.content_type.app_label     # اسم التطبيق
    #         model = perm.content_type.model             # اسم الموديل
    #         perm_name = perm.codename.split('_')[0]     # اسم الصلاحية فقط (view, add, ...)

    #         # إنشاء التطبيق إذا لم يكن موجود
    #         if app_label not in grouped:
    #             grouped[app_label] = {}

    #         # إنشاء الموديل داخل التطبيق إذا لم يكن موجود
    #         if model not in grouped[app_label]:
    #             grouped[app_label][model] = []

    #         # منع التكرار
    #         if perm_name not in grouped[app_label][model]:
    #             grouped[app_label][model].append(perm_name)
    #         print(grouped)    

    #     return Response(grouped)
    
    # @action(detail=False, methods=['get'])
    # def by_model(self, request):
    #     """تجميع الصلاحيات حسب النموذج"""
    #     permissions = Permission.objects.all().select_related('content_type')
    #     grouped = {}
        
    #     for perm in permissions:
    #         model = perm.content_type.model
    #         if model not in grouped:
    #             grouped[model] = []
    #         grouped[model].append(PermissionsSerialzer(perm).data)
    #         print(grouped)
        
    #     return Response(grouped)               
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import User
from .auth_services import force_logout_user
@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def force_logout_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    force_logout_user(user)
    ActivityLog.objects.create(
        actor=request.user,
        action_flag=ActivityLog.FORCE_LOGOUT,
        app_label='auth',
        model_name='user',
        object_id=str(user.id),
        object_repr=str(user),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )

    return Response({
        "detail": "تم إنهاء جلسات المستخدم بنجاح"
    })