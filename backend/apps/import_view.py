from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.apps import apps
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .services.import_service import ImportService
from django.utils.translation import gettext as _

class DataImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        app_label = request.data.get('app_label')
        model_name = request.data.get('model_name')
        file_obj = request.FILES.get('file')

        if not all([app_label, model_name, file_obj]):
            return Response({'detail': _("Missing parameters (app_label, model_name, file)")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return Response({'detail': _("Model not found")}, status=status.HTTP_404_NOT_FOUND)

        # Check permission: 'add' permission on the model
        perm_codename = f'{app_label}.add_{model_name.lower()}'
        if not request.user.has_perm(perm_codename):
             # Also check generic 'is_staff' or superuser if perm is missing? 
             # Standard django: user.has_perm('app.add_model')
             if not request.user.is_superuser:
                 raise PermissionDenied(_("You do not have permission to import data for this model."))

        try:
            # Initialize Service
            # We assume the API uses a specific serializer. 
            # If the ModelViewSet has get_serializer_class, we unfortunately can't verify it easily from here 
            # unless we know the ViewSet path.
            # Strategy:
            # 1. Try to find a serializer class attached to the model (custom attribute we might add).
            # 2. Or, construct a Default Serializer dynamically? (Risky for complex logic).
            # 3. Best: The caller (Frontend) could assume the Standard Serializer is used, or we try to find the module.
            
            # Let's rely on `apps/baseview.py` or `serializers.py` convention?
            # Or, let's Import existing serializers?
            
            # IMPROVEMENT:
            # We can try to import the serializer dynamically if we follow a naming convention (ModelNameSerializer).
            serializer_class = self._get_serializer_class(app_label, model_name)
            
            service = ImportService(model, serializer_class)
            result = service.handle_import(file_obj)
            
            if result['status'] == 'failed':
                 return Response(result, status=status.HTTP_400_BAD_REQUEST)
            elif result['status'] == 'error':
                 return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_serializer_class(self, app_label, model_name):
        """
        Attempt to load ModelNameSerializer from app.serializers
        """
        import importlib
        try:
            # Try apps.app_label.serializers
            module_path = f"{app_label}.serializers"
            module = importlib.import_module(module_path)
            
            # 1. Try CreateSerializer (Preferred for imports)
            serializer_name_create = f"{model_name}CreateSerializer"
            if hasattr(module, serializer_name_create):
                return getattr(module, serializer_name_create)

            # 2. Try Standard Serializer
            serializer_name_std = f"{model_name}Serializer"
            if hasattr(module, serializer_name_std):
                return getattr(module, serializer_name_std)
                
            # 3. Try Typos/Variants (optional, strictly based on finding 'UserSerialzer')
            serializer_name_typo = f"{model_name}Serialzer"
            if hasattr(module, serializer_name_typo):
                 return getattr(module, serializer_name_typo)

        except ImportError:
            pass
        
        # Fallback: Maybe 'api.serializers'?
        # Or raise error that we can't sanitize input without a serializer
        raise ValidationError(_(f"Could not find serializer for {model_name}. Ensure {model_name}CreateSerializer or {model_name}Serializer exists in {app_label}.serializers"))
