from rest_framework import viewsets, permissions
from .models import Source
from .serializers import SourceSerializer


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['source_name', 'description']
    filterset_fields = ['source_type', 'reliability_status']

