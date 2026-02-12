from argparse import Action
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from .models import *
from rest_framework.decorators import action
from rest_framework.response import Response
from api.base import UnifiedModelViewSet
from api.codes import *
class AppTypeViewSet(UnifiedModelViewSet):
    queryset = AppType.objects.all()
    serializer_class = AppTypeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    created_code = APP_TYPE_CREATED
    updated_code = APP_TYPE_UPDATED
    deleted_code = APP_TYPE_DELETED
    frozen_code = APP_TYPE_FROZEN

class AppViewSet(UnifiedModelViewSet):
    # queryset = App.objects.all()
    serializer_class = AppSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    created_code = APP_CREATED
    updated_code = APP_UPDATED
    deleted_code = APP_DELETED
    frozen_code = APP_FROZEN

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return App.objects.none()
            
        if user.is_superuser:
            return App.objects.all()
            
        # Get all permissions for the user
        # Returns set of strings: "app_label.codename"
        user_perms = user.get_all_permissions()
        
        # Extract unique app_labels
        allowed_apps = set()
        for perm in user_perms:
            try:
                app_label = perm.split('.')[0]
                allowed_apps.add(app_label)
            except IndexError:
                continue
                
        return App.objects.filter(app_label__in=allowed_apps)

   


class AppVersionViewSet(UnifiedModelViewSet):
    queryset = AppVersion.objects.all().order_by('-release_date')
    serializer_class = AppVersionSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    created_code = APP_VERSION_CREATED
    updated_code = APP_VERSION_UPDATED
    deleted_code = APP_VERSION_DELETED
    frozen_code = APP_VERSION_FROZEN