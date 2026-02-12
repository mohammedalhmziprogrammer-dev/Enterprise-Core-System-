# from functools import wraps
# from django.http import HttpResponse

# def export_response(format_type='excel'):
#     """
#     ديكورات لتبسيط التصدير من الـ Views العادية
#     """
#     def decorator(view_func):
#         @wraps(view_func)
#         def wrapper(request, *args, **kwargs):
#             # استدعاء الدالة الأصلية
#             result = view_func(request, *args, **kwargs)
            
#             # إذا كانت النتيجة QuerySet
#             if hasattr(result, 'model'):
#                 from ..services.exporter import DynamicExporter
                
#                 # معلمات التصدير من request
#                 columns = request.GET.getlist('columns') or None
#                 filename = request.GET.get('filename')
                
#                 response = DynamicExporter.export(
#                     data_source=result,
#                     export_format=format_type,
#                     columns=columns,
#                     filename=filename
#                 )
                
#                 return response
            
#             return result
#         return wrapper
#     return decorator