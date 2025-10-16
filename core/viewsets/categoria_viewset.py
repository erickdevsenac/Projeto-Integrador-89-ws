from rest_framework import viewsets 
from core.models.produto import CategoriaProduto
from core.serializers.categoria_serializer import CategoriaProdutoSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProduto.objects.all()
    serializer_class = CategoriaProdutoSerializer