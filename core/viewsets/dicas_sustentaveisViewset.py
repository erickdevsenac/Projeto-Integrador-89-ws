from rest_framework import viewsets
from core.models import Dica, CategoriaDica
from core.serializers.dicas_sustentaveisSerializer import DicaSerializer
from core.serializers.categoriaSerializer import CategoriaSerializer
class CategoriaDicaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaDica.objects.all()
    serializer_class = CategoriaSerializer

class DicaViewSet(viewsets.ModelViewSet):
    queryset = Dica.objects.all()
    serializer_class = DicaSerializer
    ordering = ['-data_publicacao'] 
