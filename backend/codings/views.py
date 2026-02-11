from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CodingCategory, Coding
from .serializers import CodingCategorySerializer, CodingSerializer

class CodingCategoryViewSet(viewsets.ModelViewSet):
    queryset = CodingCategory.objects.all()
    serializer_class = CodingCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

class CodingViewSet(viewsets.ModelViewSet):
    queryset = Coding.objects.all()
    serializer_class = CodingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
