from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Release
from .serializers import ReleaseSerializer

class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.all().order_by('-release_date')
    serializer_class = ReleaseSerializer
    permission_classes = [IsAuthenticated]
