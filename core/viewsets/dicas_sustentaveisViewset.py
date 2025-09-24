
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..models import Dica, CategoriaDica
from ..serializers import DicaSerializer, CategoriaDicaSerializer

class CategoriaDicaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDica.objects.all()
    serializer_class = CategoriaDicaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class DicaViewSet(viewsets.ModelViewSet):
    queryset = Dica.objects.all()
    serializer_class = DicaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
