from django.contrib import admin

# Register your models here.
from .models import Customer, Contact, Lead, Opportunity, Note

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    pass
@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    pass
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass