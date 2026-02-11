from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReleaseViewSet

router = DefaultRouter()
router.register(r'releases', ReleaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
