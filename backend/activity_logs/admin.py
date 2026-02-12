from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class AppTypeAdmin(admin.ModelAdmin):
    pass    
