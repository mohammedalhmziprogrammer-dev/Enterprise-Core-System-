from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, ContactViewSet, LeadViewSet,
    OpportunityViewSet, NoteViewSet
)

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"leads", LeadViewSet)
router.register(r"opportunities", OpportunityViewSet)
router.register(r"notes", NoteViewSet)


urlpatterns = [
    path('', include(router.urls)),
]


