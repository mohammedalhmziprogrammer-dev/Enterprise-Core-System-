from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodingCategoryViewSet, CodingViewSet

router = DefaultRouter()
router.register(r'categories', CodingCategoryViewSet)
router.register(r'codings', CodingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
