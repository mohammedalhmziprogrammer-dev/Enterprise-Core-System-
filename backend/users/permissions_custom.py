# from django.contrib.auth.models import Permission,User
# from django.contrib.contenttypes.models import ContentType

# from Ufuq.users.models import UserRole


# def check_permission(user,model,code_name):
#     if not user or not user.is_authenticated:
#         return False
#     if user.user_permissions.filter(
#         codename=code_name,
#         content_type=ContentType.objects.get_for_model(model)
#     ).exit():
#         return True
    
#     for groups in user.groups.all():
#         if user.permissions.filter(codename=code_name,content_type=ContentType.objects.get_for_model(model)).exit():
#             return True
        
#     if UserRole.objects.filter():
#         return  


