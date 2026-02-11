from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from .models import *

class AppTypeViewSet(viewsets.ModelViewSet):
    queryset = AppType.objects.all()
    serializer_class = AppTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class AppVersionViewSet(viewsets.ModelViewSet):
    queryset = AppVersion.objects.all().order_by('-release_date')
    serializer_class = AppVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]