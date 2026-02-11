from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path,include
router=DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'role', RoleViewSet, basename='role')
router.register(r'group', GroupViewSet, basename='group')
router.register(r'permissions', PermissionsViewSet, basename='permissions')
urlpatterns = [
    path('', include(router.urls)), 
]