from django.urls import path
from ..views.api_views import (
    ExportAPIView,
 
)
 
urlpatterns = [
    path('export/', ExportAPIView.as_view(), name='export'),  #     1
   
]