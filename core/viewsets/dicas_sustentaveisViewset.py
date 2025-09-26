from rest_framework import viewsets
from ..models import Dica, CategoriaDica
from ..serializers import DicaSerializer, CategoriaDicaSerializer

class CategoriaDicaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDica.objects.all()
    serializer_class = CategoriaDicaSerializer

class DicaViewSet(viewsets.ModelViewSet):
    queryset = Dica.objects.all()
    serializer_class = DicaSerializer
    ordering = ['-data_publicacao'] 
