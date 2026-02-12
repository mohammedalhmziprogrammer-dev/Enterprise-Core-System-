"""
Update Management Views
API endpoints for update management.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .update_models import Update, UpdateItem, ClientUpdate, UpdateLog
from .update_serializers import (
    UpdateSerializer, UpdateListSerializer, UpdateCreateSerializer,
    UpdateItemSerializer, ClientUpdateSerializer, ClientUpdateListSerializer,
    UpdateLogSerializer, ApplyUpdateSerializer
)
from .update_services import UpdateService
from apps.baseview import BaseViewSet
from api.codes import *
from api.utils import standard_response


class UpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Updates.
    """
    queryset = Update.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'update_type', 'base_release', 'is_mandatory']
    search_fields = ['name', 'version', 'description']
    ordering_fields = ['created_at', 'version', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UpdateListSerializer
        elif self.action == 'create':
            return UpdateCreateSerializer
        return UpdateSerializer
    
    
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Generate update package for deployment."""
        try:
            url = UpdateService.generate_update_package(pk, user=request.user)
            return Response({
                'success': True,
                'message': 'Update package generated successfully.',
                'url': url
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate update compatibility with a beneficiary."""
        beneficiary_id = request.data.get('beneficiary_id')
        if not beneficiary_id:
            return Response({
                'success': False,
                'message': 'beneficiary_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = UpdateService.validate_compatibility(pk, beneficiary_id)
        return Response({
            'success': result['compatible'],
            'compatible': result['compatible'],
            'message': result['message']
        })
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply update to one or more beneficiaries."""
        serializer = ApplyUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client_updates = UpdateService.apply_update(
                update_id=pk,
                beneficiary_ids=serializer.validated_data['beneficiary_ids'],
                user=request.user,
                scheduled_at=serializer.validated_data.get('scheduled_at'),
                notes=serializer.validated_data.get('notes')
            )
            
            return Response({
                'success': True,
                'message': f'Update applied to {len(client_updates)} beneficiaries.',
                'count': len(client_updates),
                'client_updates': ClientUpdateListSerializer(client_updates, many=True).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get deployment statistics for an update."""
        stats = UpdateService.get_update_stats(pk)
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for an update."""
        update = self.get_object()
        logs = update.logs.all()
        serializer = UpdateLogSerializer(logs, many=True)
        return Response(serializer.data)


class UpdateItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing UpdateItems.
    """
    queryset = UpdateItem.objects.all()
    serializer_class = UpdateItemSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['update', 'item_type', 'change_type', 'app']
    ordering = ['order']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        update_id = self.request.query_params.get('update')
        if update_id:
            queryset = queryset.filter(update_id=update_id)
        return queryset


class ClientUpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ClientUpdates.
    """
    queryset = ClientUpdate.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['update', 'beneficiary', 'status', 'client_release']
    search_fields = ['beneficiary__public_name', 'update__name']
    ordering_fields = ['scheduled_at', 'completed_at', 'status']
    ordering = ['-scheduled_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClientUpdateListSerializer
        return ClientUpdateSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark update as completed."""
        try:
            client_update = UpdateService.mark_update_completed(pk, user=request.user)
            return Response({
                'success': True,
                'message': 'Update marked as completed.',
                'data': ClientUpdateSerializer(client_update).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Mark update as failed."""
        error_message = request.data.get('error_message', 'Unknown error')
        try:
            client_update = UpdateService.mark_update_failed(pk, error_message, user=request.user)
            return Response({
                'success': True,
                'message': 'Update marked as failed.',
                'data': ClientUpdateSerializer(client_update).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """Rollback an update."""
        try:
            client_update = UpdateService.rollback_update(pk, user=request.user)
            return Response({
                'success': True,
                'message': 'Update rolled back successfully.',
                'data': ClientUpdateSerializer(client_update).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UpdateLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing UpdateLogs (read-only).
    """
    queryset = UpdateLog.objects.all()
    serializer_class = UpdateLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['update', 'client_update', 'action', 'performed_by']
    ordering = ['-performed_at']


class BeneficiaryUpdatesViewSet(viewsets.ViewSet):
    """
    ViewSet for getting updates related to a specific beneficiary.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    
    def list(self, request, beneficiary_pk=None):
        """Get all updates (pending and applied) for a beneficiary."""
        # Pending updates
        pending = UpdateService.get_pending_updates_for_beneficiary(beneficiary_pk)
        
        # Applied updates
        applied = ClientUpdate.objects.filter(
            beneficiary_id=beneficiary_pk
        ).order_by('-scheduled_at')
        
        return Response({
            'pending_updates': UpdateListSerializer(pending, many=True).data,
            'applied_updates': ClientUpdateListSerializer(applied, many=True).data
        })
