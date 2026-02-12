
from typing import override
from django.shortcuts import render
from django.test import Client
from django_filters.rest_framework import filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import *
from .models import *
from rest_framework import viewsets, permissions,filters
from rest_framework.response import Response
from users.permissions_utils import *
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import action
# from api.base import UnifiedModelViewSet
from apps.baseview import BaseViewSet
from api.codes import *
from api.utils import standard_response

@action(detail=True, methods=["post"])
def freeze(self, request, pk=None):
    side = self.get_object()
    if side.action=="destroy":
        side.is_active = False
        side.save()
        return standard_response(BENEFICIARY_FROZEN)
    
def get_all_parent_structure(node):
    parent=[node]
    while node.structure is not None:
        node=node.structure
        parent.append(node)
    return reversed(parent)  

def get_all_children_structure(node):
    children=list(node.children.all())
    for child in node.children.all():
        children.extend(get_all_children_structure(child))
    return children 


class BeneficiaryViewSet(BaseViewSet):
    queryset=Beneficiary.objects.all()
    serializer_class=BeneficiarySerializer
    permission_classes=[permissions.DjangoModelPermissions,permissions.IsAuthenticated]
    created_code = BENEFICIARY_CREATED
    updated_code = BENEFICIARY_UPDATED
    deleted_code = BENEFICIARY_DELETED
    frozen_code = BENEFICIARY_FROZEN
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['public_name', 'pravite_name', 'order']
    search_fields = ['public_name']
    ordering_fields = ['order']
    ordering = ['order']
    
    @action(detail=True, methods=['get'])
    def structure(self,requset,pk=None):
        benefi=self.get_object()
        structure=benefi.beneficiary_structure.all()
        serializer=StructureSerializer(structure,many=True)
        return Response(serializer.data)
       
  

class LevelViewSet(BaseViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    created_code = LEVEL_CREATED
    updated_code = LEVEL_UPDATED
    deleted_code = LEVEL_DELETED
    frozen_code = LEVEL_FROZEN
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
   
    
class StructureViewSet(BaseViewSet):
    queryset=Structure.objects.all()
    serializer_class=StructureSerializer
    permission_classes=[permissions.IsAuthenticated,permissions.DjangoModelPermissions]
    created_code = STRUCTURE_CREATED
    updated_code = STRUCTURE_UPDATED
    deleted_code = STRUCTURE_DELETED
    frozen_code = STRUCTURE_FROZEN
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'order']
    search_fields = ['name']
    ordering_fields = ['order']
    ordering = ['order']
    
  
    def structure(self,request,pk=None):
        str_obj=self.get_object()
        # Assuming user is related to structure somehow, but based on models, it's not directly there.
        # The original code had str.user.username, but Structure model doesn't have user field.
        # I will comment this out or fix it if I find the relation.
        # For now, let's just return the object data.
        return Response(StructureSerializer(str_obj).data)
    
    @action(detail=False, methods=['get'])
    def tree(self, request, *args, **kwargs):
        # Optimized O(N) tree generation
        structures = Structure.objects.all()
        serializer = StructureSerializer(structures, many=True)
        data = serializer.data

        # Create a map of items by ID
        item_map = {item['id']: item for item in data}
        
        # Initialize children list for each item
        for item in data:
            item['children'] = []

        tree = []
        for item in data:
            parent_id = item.get('structure') # 'structure' is the foreign key to parent
            if parent_id:
                parent = item_map.get(parent_id)
                if parent:
                    parent['children'].append(item)
                else:
                    # Parent not found (orphan), treat as root or handle error
                    tree.append(item) 
            else:
                tree.append(item)
        
        return Response(tree)

    @action(detail=True, methods=['get'], url_path='children')
    def get_children(self, request, pk=None):
        try:
            structure = self.get_object()
            # Get all descendants recursively
            children = get_all_children_structure(structure)
            serializer = StructureSerializer(children, many=True)
            return Response(serializer.data)
        except Structure.DoesNotExist:
             return standard_response(NOT_FOUND, success=False, status_code=404)

    @action(detail=True, methods=['get'], url_path='parent')
    def get_parent(self, request, pk=None):
        try:
            structure = self.get_object()
            # Get path to root (ancestors)
            parents = get_all_parent_structure(structure)
            # Convert generator to list if needed, or iterate
            parents_list = list(parents)
            serializer = StructureSerializer(parents_list, many=True)
            return Response(serializer.data)
        except Structure.DoesNotExist:
             return standard_response(NOT_FOUND, success=False, status_code=404)
    
    # -----------------------------
    # هذا هو التعديل  
    # -----------------------------
    def get_serializer_context(self):
        return {'request': self.request}
