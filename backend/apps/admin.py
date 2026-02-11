from .models import AppType,App,AppVersion,Model
from django.contrib import admin

@admin.register(AppType)
class AppTypeAdmin(admin.ModelAdmin):
    pass    

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    pass    

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    pass    

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    pass    

