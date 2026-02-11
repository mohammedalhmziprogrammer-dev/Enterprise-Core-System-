from django.urls import include, path
from rest_framework import routers
from .views import BeneficiaryViewSet, LevelViewSet, StructureViewSet
router = routers.DefaultRouter()
router.register(r'beneficiaries', BeneficiaryViewSet, basename='beneficiary')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'structures', StructureViewSet, basename='structure')
# router.register(r'StrcuterUsers',  StrcuterUsersViewSet, basename='StrcuterUsers')

urlpatterns = [
    path('', include(router.urls)), 
]