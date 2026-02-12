from rest_framework import viewsets, status
from rest_framework.response import Response
from .utils import standard_response
from .codes import *
from django.db.models import ProtectedError

class UnifiedModelViewSet(viewsets.ModelViewSet):
    """
    A ViewSet that provides standardized responses for create, update, and destroy actions.
    Subclasses should define:
    - created_code
    - updated_code
    - deleted_code
    """
    created_code = ACTION_SUCCESS
    updated_code = ACTION_SUCCESS
    deleted_code = ACTION_SUCCESS
    frozen_code = ACTION_SUCCESS

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
             return standard_response(VALIDATION_ERROR, serializer.errors, success=False, status_code=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return standard_response(self.created_code, serializer.data, status_code=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
             return standard_response(VALIDATION_ERROR, serializer.errors, success=False, status_code=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return standard_response(self.updated_code, serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        try:
            # First, attempt a Hard Delete
            self.perform_destroy(instance)
            return standard_response(self.deleted_code, status_code=status.HTTP_200_OK)
            
        except ProtectedError:
            # If ProtectedError is raised (foreign key constraint), fallback to Soft Delete (Freeze)
            if hasattr(instance, 'is_active'):
                instance.is_active = False
                instance.save()
                return standard_response(self.frozen_code, status_code=status.HTTP_200_OK)
            else:
                # If cannot be frozen (no is_active), re-raise
                raise
 