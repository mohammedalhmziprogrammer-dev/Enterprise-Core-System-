from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.apps import apps

from ..services.exporter import DynamicExporter

class ExportAPIView(APIView):
    """
    واجهة API مركزية للتصدير
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        تصدير البيانات
        """
        try:
            data = request.data
            
            if not data:
                return Response(
                    {'error': 'لم يتم إرسال أي بيانات'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'data' in data and isinstance(data['data'], list):
                return self._export_direct_data(data)
            
            model_path = data.get('model')
            if not model_path:
                return Response(
                    {'error': 'يجب تحديد نموذج البيانات أو إرسال بيانات مباشرة'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            export_format = data.get('format', 'excel')
            columns = data.get('columns', [])
            filters = data.get('filters', {})
            filename = data.get('filename')
            title = data.get('title')
            
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
            except (ValueError, LookupError):
                return Response(
                    {'error': f'النموذج {model_path} غير موجود'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                response = DynamicExporter.export(
                    data_source=model_path,
                    export_format=export_format,
                    columns=columns,
                    filters=filters,
                    user=request.user,
                    filename=filename,
                    title=title
                )
                return response
            except Exception as e:
                return Response(
                    {'error': f'خطأ في التصدير: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            return Response(
                {'error': f'خطأ غير متوقع: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _export_direct_data(self, data):
        """تصدير بيانات مباشرة بدون موديل"""
        export_data = data.get('data', [])
        export_format = data.get('format', 'excel')
        columns = data.get('columns', [])
        filename = data.get('filename')
        title = data.get('title')
        
        if not isinstance(export_data, list):
            return Response(
                {'error': 'يجب أن تكون البيانات قائمة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(export_data) == 0:
            return Response(
                {'error': 'لا توجد بيانات للتصدير'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            response = DynamicExporter.export(
                data_source=export_data,
                export_format=export_format,
                columns=columns,
                filename=filename,
                title=title
            )
            return response
        except Exception as e:
            return Response(
                {'error': f'خطأ في التصدير: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )