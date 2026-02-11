from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppViewSet, AppTypeViewSet, AppVersionViewSet

router = DefaultRouter()
router.register(r'apps', AppViewSet)
router.register(r'types', AppTypeViewSet)
router.register(r'versions', AppVersionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
