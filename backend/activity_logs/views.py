from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ActivityLog
from .serializers import ActivityLogSerializer

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all().select_related('actor')
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated,] # Adjust as needed, maybe IsAdminUser?
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['actor', 'action_flag', 'app_label', 'model_name']
    search_fields = ['object_repr', 'changes', 'ip_address']
    ordering_fields = ['action_time', 'actor']
    ordering = ['-action_time']

    def get_queryset(self):
        user = self.request.user
        queryset = ActivityLog.objects.all().select_related('actor')
        
        # إذا كان المستخدم مسؤولاً (Superuser)، يرى كل السجلات
        if user.is_superuser:
            return queryset
            
        # للمستخدمين العاديين، يتم إرجاع سجلاتهم فقط تلقائياً وبأمان
        return queryset.filter(actor=user)
    # def create(self,requset):
    #     self.request.META.__dict__