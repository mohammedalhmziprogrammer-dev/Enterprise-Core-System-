# users/management/commands/create_custom_permissions.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_permission_codename
from django.conf import settings

class Command(BaseCommand):
    help = "إنشاء جميع الصلاحيات المخصصة المحددة في CUSTOM_DEFAULT_PERMISSIONS"

    def handle(self, *args, **kwargs):
        custom_perms = getattr(settings, 'CUSTOM_DEFAULT_PERMISSIONS', ())

        if not custom_perms:
            self.stdout.write(self.style.WARNING("لا توجد صلاحيات مخصصة في الإعدادات."))
            return

        created_count = 0
        for model in apps.get_models():
            content_type = ContentType.objects.get_for_model(model)
            for perm in custom_perms:
                codename = get_permission_codename(perm, model._meta)

                # تحقق من عدم وجود الصلاحية مسبقًا
                if Permission.objects.filter(content_type=content_type, codename=codename).exists():
                    continue

                name = f"Can {perm} {model._meta.verbose_name}"
                Permission.objects.create(
                    content_type=content_type,
                    codename=codename,
                    name=name,
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ تم إنشاء {created_count} صلاحيات جديدة."))
