from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Release
from .serializers import ReleaseSerializer
from .services import ReleaseExportService

class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        release = self.get_object()
        try:
            service = ReleaseExportService(release.id)
            file_url = service.generate_export()
            return Response({'status': 'success', 'file_url': file_url})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        release = self.get_object()
        try:
            from .services import ReleaseService
            ReleaseService.activate_release(release.id)
            return Response({'status': 'success', 'message': 'Release activated successfully'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_to_client(self, request, pk=None):
        release = self.get_object()
        beneficiary_id = request.data.get('beneficiary_id')
        if not beneficiary_id:
            return Response({'status': 'error', 'message': 'beneficiary_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .services import ReleaseService
            ReleaseService.assign_to_client(release, beneficiary_id)
            return Response({'status': 'success', 'message': 'Release assigned to client successfully'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def download_source(self, request, pk=None):
        release = self.get_object()
        
        # Restriction: Check if assigned to at least one entity
        if not release.clientrelease_set.filter(is_active=True).exists():
             return Response({'status': 'error', 'message': 'Cannot download unassigned release. Please assign to a client first.'}, status=status.HTTP_403_FORBIDDEN)
             
        try:
            from .services import ReleaseExportService
            from django.http import FileResponse
            import os
            
            service = ReleaseExportService(release.id)
            # generate_source_export now returns the URL, but the file is in release.exported_file
            # We can rely on the service to ensure the file exists.
            service.generate_source_export()
            
            if release.exported_file:
                # Open the file handler
                response = FileResponse(release.exported_file.open('rb'), as_attachment=True, filename=os.path.basename(release.exported_file.name))
                return response
            else:
                return Response({'status': 'error', 'message': 'File generation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
