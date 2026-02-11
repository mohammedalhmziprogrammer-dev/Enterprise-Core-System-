
from .models import Beneficiary,Level,Structure 
from django.contrib import admin

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    readonly_fields=['order']
    pass    

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass    

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass    
