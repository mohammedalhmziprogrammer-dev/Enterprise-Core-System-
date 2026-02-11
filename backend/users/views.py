from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from .models import *
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework import viewsets, status, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.contrib.contenttypes.models import ContentType

# User ViewSet with comprehensive functionality
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('direct_manager').prefetch_related('stractures', 'groups')
    permission_classes = [permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'data_visibility', 'must_change_password']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined', 'last_login', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerialzer
    # def create(self, request, *args, **kwargs):
    #     serializers=UserCreateSerializer(data=request.data)
    #     if serializers.is_valid():
    #      phone=serializers.validated_data['phone']
    #      check=check_phone_number(phone)
    #      if not check:
    #            return Response({'error': '    الهاتف'}
    #                )
          
    #     return super().create(request, *args, **kwargs)
         
    
    def get_queryset(self):
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
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """تغيير كلمة مرور المستخدم الحالي"""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'كلمة المرور القديمة غير صحيحة'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.must_change_password = False
            user.save()
            return Response({'status': 'تم تغيير كلمة المرور بنجاح'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """إعادة تعيين كلمة مرور المستخدم"""
        user = self.get_object()
        new_password = request.data.get('new_password', 'password123')
        user.set_password(new_password)
        user.must_change_password = True
        user.save()
        return Response({'status': 'تم إعادة تعيين كلمة المرور بنجاح'})
    
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """تعيين أدوار للمستخدم"""
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        roles = Role.objects.filter(id__in=role_ids)
        user.groups.clear()
        for role in roles:
            if role.group:
                user.groups.add(role.group)
        
        return Response({
            'status': 'تم تعيين الأدوار بنجاح',
            'roles': RoleSerialzer(roles, many=True).data
        })
    
    # @action(detail=True, methods=['post'])
    # def assign_group(self, request, pk=None):
    #     """تعيين أدوار للمستخدم"""
    #     user = self.get_object()
    #     group_ids = request.data.get('group_ids', [])
        
    #     group = Group.objects.filter(id__in=rolgroup_idse_ids)
    #     user.groups.clear()
    #     for role in roles:
    #         if role.group:
    #             user.groups.add(role.group)
        
    #     return Response({
    #         'status': 'تم تعيين الأدوار بنجاح',
    #         'roles': RoleSerialzer(roles, many=True).data
    #     })
    
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
    
    @action(detail=True, methods=['post'])
    def assign_structures(self, request, pk=None):
        """تعيين هياكل إدارية للمستخدم"""
        user = self.get_object()
        structure_ids = request.data.get('structure_ids', [])
        
        from clients.models import Structure
        structures = Structure.objects.filter(id__in=structure_ids)
        user.stractures.set(structures)
        
        return Response({'status': 'تم تعيين الهياكل الإدارية بنجاح'})
    
    @action(detail=True, methods=['post'])
    def assign_groups(self, request, pk=None):
        """تعيين هياكل إدارية للمستخدم"""
        user = self.get_object()
        group_ids = request.data.get('group_ids', [])
        groups = Group.objects.filter(id__in=group_ids)
        user.groups.set(groups)
        
        return Response({'status': 'تم تعيين المجموعات  بنجاح'})
    
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


# Role ViewSet with enhanced functionality
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().prefetch_related('permissions', 'codingCategory', 'coding')
    serializer_class = RoleSerialzer
    permission_classes = [permissions.IsAuthenticated ,permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """تعيين صلاحيات للدور"""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        role.permissions.set(permissions)
        
        return Response({
            'status': 'تم تعيين الصلاحيات بنجاح',
            'permissions': PermissionsSerialzer(permissions, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """الحصول على المستخدمين المعينين لهذا الدور"""
        role = self.get_object()
        roles=role.group
        if role.group:
            users = User.objects.filter(groups=roles)
            return Response(UserSerialzer(users, many=True).data)
        return Response([])
    
    @action(detail=True, methods=['post'])
    def assign_coding_categories(self, request, pk=None):
        """تعيين فئات الترميز للدور"""
        role = self.get_object()
        category_ids = request.data.get('category_ids', [])
        
        from codings.models import CodingCategory
        categories = CodingCategory.objects.filter(id__in=category_ids)
        role.codingCategory.set(categories)
        
        return Response({'status': 'تم تعيين فئات الترميز بنجاح'})
    
    @action(detail=True, methods=['post'])
    def assign_codings(self, request, pk=None):
        """تعيين رموز للدور"""
        role = self.get_object()
        coding_ids = request.data.get('coding_ids', [])
        
        from codings.models import Coding
        codings = Coding.objects.filter(id__in=coding_ids)
        role.coding.set(codings)
        
        return Response({'status': 'تم تعيين الرموز بنجاح'})


# Group ViewSet with enhanced functionality
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().prefetch_related('permissions')
    serializer_class = GroupSerialzer
    permission_classes = [permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    
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
        
        return Response({
            'status': 'تم تعيين الصلاحيات بنجاح',
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


# Permission ViewSet with enhanced functionality
class PermissionsViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().select_related('content_type')
    serializer_class = PermissionsSerialzer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type']
    search_fields = ['name', 'codename']
    ordering_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']
    
    @action(detail=False, methods=['get'])
    def by_app(self, request):
        """تجميع الصلاحيات حسب التطبيق"""
        permissions = Permission.objects.all().select_related('content_type')
        grouped = {}
         
        for perm in permissions:
            app_label = perm.content_type.app_label
            if app_label not in grouped:
                grouped[app_label] = []
            grouped[app_label].append(PermissionsSerialzer(perm).data)
        
        return Response(grouped)
    
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
