from django.apps import AppConfig
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'


    def ready(self):        
        import users.signals

   

        # إنشاء الصلاحيات المخصصة عند تشغيل التطبيق
      