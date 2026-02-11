from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

# from users.models import UserRole


def get_permissions_for_model(model):
    content_type = ContentType.objects.get_for_model(model)
    return Permission.objects.filter(content_type=content_type)

def user_has_permission(user, perm_codename, model):
    print("Checking permission:", user, perm_codename, model)
    if not user.is_authenticated:
        return False
    contenttype=ContentType.objects.get_for_model(model)
    perm_full_codename=f"{contenttype.app_label}.{perm_codename}"
    return user.has_perm(perm_full_codename)

def group_has_permission(groups, perm_codename, model):
    """يتحقق مما إذا كانت أي مجموعة من مجموعات المستخدم تمتلك الصلاحية."""
    content_type = ContentType.objects.get_for_model(model)
    for group in groups:
        if group.permissions.filter(
            codename=perm_codename,
            content_type=content_type
        ).exists():
            print("Allowed via group:", group)
            return True
    return False
def role_has_permission(role_or_roles, perm_codename, model):
    """يتحقق مما إذا كان الدور أو أي من الأدوار يمتلك الصلاحية."""
    print("Allowed via role:", role)
    if not role_or_roles:
        return False

    # تحويل الدور المفرد إلى قائمة إذا لزم الأمر
    roles = [role_or_roles] if not hasattr(role_or_roles, '__iter__') else role_or_roles

    content_type = ContentType.objects.get_for_model(model)
    for role in roles:
        if role.permissions.filter(codename=perm_codename, content_type=content_type).exists():
            return True
    return False
def has_permission(user, perm_codename, model):
    if not user or not user.is_authenticated:
        return False

    # صلاحيات المستخدم المباشرة
    if user.user_permissions.filter(
        codename=perm_codename,
        content_type=ContentType.objects.get_for_model(model)
    ).exists():
        return True

    # صلاحيات المجموعات
    for group in user.groups.all():
        if group.permissions.filter(
            codename=perm_codename,
            content_type=ContentType.objects.get_for_model(model)
        ).exists():
            return True

    
    # صلاحيات الأدوار
    roles = getattr(user, 'roles', [])
    if roles:
        # إذا roles QuerySet فارغ، لن تدخل الحلقة
        if hasattr(roles, 'all'):
            roles = roles.all()
        for role in roles:
            if role.permissions.filter(
                codename=perm_codename,
                content_type=ContentType.objects.get_for_model(model)
            ).exists():
                return True

    return False  # هنا فقط نرجع False إذا لا يوجد صلاحية

def assign_permission_to_user(user, perm_codename, model):
    permissions = get_permissions_for_model(model)
    try:
        permission = permissions.get(codename=perm_codename)
        user.user_permissions.add(permission)
        return True
    except Permission.DoesNotExist:
        return False
    
def assign_permission_to_group(group, perm_codename, model):
    permissions = get_permissions_for_model(model)
    try:
        permission = permissions.get(codename=perm_codename)
        group.permissions.add(permission)
        return True
    except Permission.DoesNotExist:
        return False
def remove_permission_from_user(user, perm_codename, model):
    permissions = get_permissions_for_model(model)
    try:
        permission = permissions.get(codename=perm_codename)
        user.user_permissions.remove(permission)
        return True
    except Permission.DoesNotExist:
        return False
def remove_permission_from_group(group, perm_codename, model):
    permissions = get_permissions_for_model(model)
    try:
        permission = permissions.get(codename=perm_codename)
        group.permissions.remove(permission)
        return True
    except Permission.DoesNotExist:
        return False
    
def list_permissions_for_user(user):
    return user.user_permissions.all()

def list_permissions_for_group(group):
    return group.permissions.all()

def list_all_permissions_for_model(model):
    return get_permissions_for_model(model)


def create_custom_permission(model, codename, name):
    content_type = ContentType.objects.get_for_model(model)
    permission, created = Permission.objects.get_or_create(
        codename=codename,
        name=name,
        content_type=content_type
    )
    return permission, created

def create_dynamic_permissions(models):
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = [
            ('view_' + model._meta.model_name, 'Can view ' + model._meta.verbose_name),
            ('add_' + model._meta.model_name, 'Can add ' + model._meta.verbose_name),
            ('change_' + model._meta.model_name, 'Can change ' + model._meta.verbose_name),
            ('delete_' + model._meta.model_name, 'Can delete ' + model._meta.verbose_name),
        ]
        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            
def create_dynamic_permissions(app_label,model_name,permissions):
    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    for codename, name in permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )

def create_privilge_custom(app_label,model,name,code):
    app_label=app_label
    model=model
    content_type = ContentType.objects.get(app_label=app_label, model=model)
    permission, created = Permission.objects.get_or_create(
        codename=code,
        name=name,
        content_type=content_type
    )
    return permission, created
def delete_custom_permission(model, codename):
    content_type = ContentType.objects.get_for_model(model)
    try:
        permission = Permission.objects.get(
            codename=codename,
            content_type=content_type
        )
        permission.delete()
        return True
    except Permission.DoesNotExist:
        return False
def delete_privilge_custom(app_label,model,code):
    content_type = ContentType.objects.get(app_label=app_label, model=model)
    try:
        permission = Permission.objects.get(
            codename=code,
            content_type=content_type
        )
        permission.delete()
        return True
    except Permission.DoesNotExist:
        return False
    
def list_all_permissions_for_model(model):
    return get_permissions_for_model(model)
def create_dynamic_permissions_for_app(app_label):
    models = ContentType.objects.filter(app_label=app_label)
    for content_type in models:
        model = content_type.model_class()
        permissions = [
            ('view_' + model._meta.model_name, 'Can view ' + model._meta.verbose_name),
            ('add_' + model._meta.model_name, 'Can add ' + model._meta.verbose_name),
            ('change_' + model._meta.model_name, 'Can change ' + model._meta.verbose_name),
            ('delete_' + model._meta.model_name, 'Can delete ' + model._meta.verbose_name),
        ]
        for codename, name in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )

