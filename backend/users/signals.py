from django.db.models.signals import post_save
from django.dispatch import receiver
# from .models import UserRole

# @receiver(post_save, sender=UserRole)
# def update_user_groups_after_role_change(sender, instance, **kwargs):
#     """تحديث مجموعات المستخدم تلقائيًا بعد تغيير الدور"""
#     if instance.role and instance.user:
#         user = instance.user
#         role = instance.role

#         # حذف المجموعات القديمة وإضافة الجديدة
#         user.groups.clear()
#         user.groups.add(role.group)
#         user.save()