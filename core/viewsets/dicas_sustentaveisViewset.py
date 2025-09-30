from rest_framework import viewsets
from core.models import Dica, CategoriaDica, Categoria
from core.serializers import DicaSerializer

class CategoriaDicaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDica.objects.all()
    serializer_class = Categoria

class DicaViewSet(viewsets.ModelViewSet):
    queryset = Dica.objects.all()
    serializer_class = DicaSerializer
    ordering = ['-data_publicacao'] 
