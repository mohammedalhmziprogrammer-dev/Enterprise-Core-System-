import csv
import pandas as pd
from django.db import transaction
from django.core.files.base import ContentFile
from rest_framework.serializers import ValidationError

class ImportService:
    def __init__(self, model, serializer_class=None):
        self.model = model
        self.serializer_class = serializer_class or self._resolve_serializer()

    def _resolve_serializer(self):
        # Try to find a serializer from the model
        if hasattr(self.model, 'get_serializer_class'):
            return self.model.get_serializer_class()
        # Fallback logic if needed, or raise error
        raise ValueError(f"No serializer found for model {self.model.__name__}")

    def handle_import(self, file_obj):
        """
        Main entry point.
        Returns: { 'success': int, 'errors': list, 'total': int }
        """
        rows = self._parse_file(file_obj)
        total_rows = len(rows)
        errors = []
        validated_data_list = []

        # 1. Validation Phase
        for index, row in enumerate(rows):
            # Row index starts at 1 usually for users (header is 0)
            line_number = index + 2 
            
            serializer = self.serializer_class(data=row)
            if serializer.is_valid():
                validated_data_list.append(serializer.validated_data)
            else:
                # Format errors
                row_errors = serializer.errors
                formatted_errors = self._format_errors(row_errors, line_number)
                errors.extend(formatted_errors)

        # 2. Atomic Save Phase
        if errors:
            return {
                'success': 0,
                'errors': errors,
                'total': total_rows,
                'status': 'failed'
            }
        
        try:
            with transaction.atomic():
                self._bulk_save(validated_data_list)
        except Exception as e:
             return {
                'success': 0,
                'errors': [{'line': '-', 'field': 'global', 'message': str(e)}],
                'total': total_rows,
                'status': 'error'
            }

        return {
            'success': len(validated_data_list),
            'errors': [],
            'total': total_rows,
            'status': 'success'
        }

    def _parse_file(self, file_obj):
        name = file_obj.name
        if name.endswith('.csv'):
            return self._parse_csv(file_obj)
        elif name.endswith('.xlsx') or name.endswith('.xls'):
            return self._parse_excel(file_obj)
        else:
            raise ValidationError("Unsupported file format. Please upload .csv or .xlsx")

    def _parse_csv(self, file_obj):
        # Decode if necessary
        file_data = file_obj.read().decode('utf-8-sig')
        reader = csv.DictReader(file_data.splitlines())
        return list(reader)

    def _parse_excel(self, file_obj):
        # Use pandas for robustness with Excel
        df = pd.read_excel(file_obj)
        # Convert NaN to None or empty string as appropriate for DRF
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')

    def _format_errors(self, errors, line_number):
        """
        Flatten DRF errors into a list of dicts: {line, field, message}
        """
        error_list = []
        for field, messages in errors.items():
            for msg in messages:
                error_list.append({
                    'line': line_number,
                    'field': field,
                    'message': str(msg) # Ensure string
                })
        return error_list

    def _bulk_save(self, validated_data_list):
        # We start with simple save in loop to trigger signals/save methods (like creating user profile etc)
        # Bulk_create doesn't trigger signals. User requested "full validation" and generic use.
        # Ideally, we loop and save.
        for data in validated_data_list:
            # Check if we should update or create?
            # For now, simplistic "create only" or "upsert"?
            # Prompt says "Import settings... dynamically defined", but let's default to Create.
            # If serializer defines .create(), it will work.
            
            # Use serializer.save() to leverage serializer's create/update logic
            # Use a dummy instance if needed? No, passing data to serializer(data=...) creates unbounded.
            # We already validated. Re-instantiate to save?
            
            # Re-instantiating serializer for saving is safer to ensure all context (like hashing password) is handled by serializer.create()
            # If we just took validated_data and Model.objects.create(**data), we skip Serializer.create() custom logic (like set_password).
            
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
