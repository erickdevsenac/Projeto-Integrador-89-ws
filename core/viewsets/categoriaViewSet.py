from rest_framework import permissions, viewsets

from core.models import Categoria
from core.serializers import (CategoriaSerializer)

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    Endpoint da API para visualizar e editar categorias de produtos.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAdminUser] 
    lookup_field = 'slug' 