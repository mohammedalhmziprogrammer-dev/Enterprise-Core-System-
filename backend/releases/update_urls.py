"""
Update Management URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .update_views import (
    UpdateViewSet, UpdateItemViewSet, ClientUpdateViewSet, 
    UpdateLogViewSet, BeneficiaryUpdatesViewSet
)

router = DefaultRouter()
router.register(r'updates', UpdateViewSet, basename='update')
router.register(r'update-items', UpdateItemViewSet, basename='update-item')
router.register(r'client-updates', ClientUpdateViewSet, basename='client-update')
router.register(r'update-logs', UpdateLogViewSet, basename='update-log')

urlpatterns = [
    path('', include(router.urls)),
    path('beneficiary/<int:beneficiary_pk>/updates/', 
         BeneficiaryUpdatesViewSet.as_view({'get': 'list'}), 
         name='beneficiary-updates'),
]
