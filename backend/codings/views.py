from apps.baseview import BaseViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CodingCategory, Coding
from .serializers import CodingCategorySerializer, CodingSerializer, CodingTreeSerializer
from django.db.models import Q, F
from api.codes import *

from django.db.models import ProtectedError
from rest_framework import status  # ⬅️ أضفه مع الاستيرادات الأخرى

class CodingCategoryViewSet(BaseViewSet):
    queryset = CodingCategory.objects.all()
    serializer_class = CodingCategorySerializer
    permission_classes = [IsAuthenticated]
    created_code = CODING_CATEGORY_CREATED
    updated_code = CODING_CATEGORY_UPDATED
    deleted_code = CODING_CATEGORY_DELETED
    frozen_code = CODING_CATEGORY_FROZEN
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response({
                "code": "CODING.CODING_CATEGORY_DELETED",
                "data": None,
                "status": "success",
                "message": "تم حذف التصنيف بنجاح"
            }, status=status.HTTP_200_OK)
        except ProtectedError as e:
            # عرض رسالة فقط عند وجود ارتباطات تمنع الحذف
            return Response(
                {"message": "لا يمكن حذف التصنيف لأنه مرتبط بعناصر أخرى."},
                status=status.HTTP_400_BAD_REQUEST
            ) 

class CodingViewSet(BaseViewSet):
    queryset = Coding.objects.all()
    serializer_class = CodingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['codingCategory', 'is_active']
    search_fields = ['name', 'category']
    ordering_fields = ['order', 'name']
    created_code = CODING_CREATED
    updated_code = CODING_UPDATED
    deleted_code = CODING_DELETED
    frozen_code = CODING_FROZEN

    def get_queryset(self):
        qs = super().get_queryset()
        # Optional: Filter by specific category name if passed
        category_name = self.request.query_params.get('category_name')
        if category_name:
            qs = qs.filter(codingCategory__specific_name=category_name)
        return qs

    @action(detail=False, methods=['get'])
    def roots(self, request):
        """
        Returns only top-level (root) items, optionally filtered by category.
        If an item has a parent but that parent belongs to a different category,
        treat it as a root for the current category context.
        """
        qs = self.filter_queryset(self.get_queryset())
        # Show if parent is null OR parent is in a different category
        qs = qs.filter(Q(parent__isnull=True) | ~Q(parent__codingCategory=F('codingCategory')))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Returns the full tree structure.
        """
        qs = self.filter_queryset(self.get_queryset())
        # Show if parent is null OR parent is in a different category
        qs = qs.filter(Q(parent__isnull=True) | ~Q(parent__codingCategory=F('codingCategory')))
        serializer = CodingTreeSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """
        Returns direct children of a specific node.
        """
        obj = self.get_object()
        children = obj.children.all().order_by('order', 'name')
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
