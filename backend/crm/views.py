from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Customer, Contact, Lead, Opportunity, Note
from .serializers import (
    CustomerSerializer, ContactSerializer, LeadSerializer,
    OpportunitySerializer, NoteSerializer
)
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.baseview import BaseViewSet
from api.codes import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend

class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.DjangoModelPermissions, permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "email", "phone", "website"]
    
    created_code = CUSTOMER_CREATED
    updated_code = CUSTOMER_UPDATED
    deleted_code = CUSTOMER_DELETED
    frozen_code = CUSTOMER_FROZEN

class ContactViewSet(BaseViewSet):
    queryset = Contact.objects.select_related("customer").all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.DjangoModelPermissions, permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "email", "phone", "position", "customer__name"]
    filterset_fields = ["customer"]
    
    created_code = CONTACT_CREATED
    updated_code = CONTACT_UPDATED
    deleted_code = CONTACT_DELETED
    frozen_code = CONTACT_FROZEN

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.request.query_params.get("customer")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs


class LeadViewSet(BaseViewSet):
    queryset = Lead.objects.select_related("owner", "converted_customer").all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.DjangoModelPermissions, permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "company_name", "email", "phone", "status", "source"]
    filterset_fields = ["status", "owner", "source"]
    
    created_code = LEAD_CREATED
    updated_code = LEAD_UPDATED
    deleted_code = LEAD_DELETED
    frozen_code = LEAD_FROZEN

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter logic is improved by filterset_fields/DjangoFilterBackend but leaving manual if complex
        # Leaving manual override as well to be safe or if specific logic needed
        return qs


class OpportunityViewSet(BaseViewSet):
    queryset = Opportunity.objects.select_related("customer", "lead", "owner").all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.DjangoModelPermissions, permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "stage", "customer__name", "lead__full_name"]
    filterset_fields = ["stage", "customer", "owner"]
    
    created_code = OPPORTUNITY_CREATED
    updated_code = OPPORTUNITY_UPDATED
    deleted_code = OPPORTUNITY_DELETED
    frozen_code = OPPORTUNITY_FROZEN

    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class NoteViewSet(BaseViewSet):
    queryset = Note.objects.select_related("customer", "lead", "opportunity", "created_by").all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.DjangoModelPermissions, permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content"]
    filterset_fields = ["customer", "lead", "opportunity"]
    
    created_code = NOTE_CREATED
    updated_code = NOTE_UPDATED
    deleted_code = NOTE_DELETED
    frozen_code = NOTE_FROZEN

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs
