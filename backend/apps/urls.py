from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppViewSet, AppTypeViewSet, AppVersionViewSet
from .import_view import DataImportView

router = DefaultRouter()
router.register(r'apps', AppViewSet,     basename='app')
router.register(r'types', AppTypeViewSet, basename='app_type')
router.register(r'versions', AppVersionViewSet, basename='app_version')

urlpatterns = [
    path('import/', DataImportView.as_view(), name='data-import'),
    path('', include(router.urls)),
]
