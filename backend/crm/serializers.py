from apps.baseserializer import BaseRulesSerializer
from apps.validation.validators import required, email, min_len
from .models import Customer, Contact, Lead, Opportunity, Note
from rest_framework import serializers

class CustomerSerializer(BaseRulesSerializer):
    RULES = {
        "name": [(required,), (min_len, 3)],
        "email": [(email,)]
    }
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class ContactSerializer(BaseRulesSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    RULES = {
        "full_name": [(required,), (min_len, 3)],
        "customer": [(required,)],
        "email": [(email,)]
    }

    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class LeadSerializer(BaseRulesSerializer):
    converted_customer_name = serializers.CharField(source="converted_customer.name", read_only=True)
    RULES = {
        "full_name": [(required,), (min_len, 3)],
        "email": [(email,)]
    }

    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class OpportunitySerializer(BaseRulesSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    lead_name = serializers.CharField(source="lead.full_name", read_only=True)
    RULES = {
        "title": [(required,), (min_len, 3)],
        "customer": [(required,)],
        "stage": [(required,)]
    }

    class Meta:
        model = Opportunity
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")



class NoteSerializer(BaseRulesSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    RULES = {
        "content": [(required,)]
    }
    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "created_by")
