from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..models import Produto
from ..serializers import ProdutoListSerializer, ProdutoDetailSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e gerenciar Produtos.
    """
    queryset = Produto.objects.disponiveis()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProdutoListSerializer
        return ProdutoDetailSerializer

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user.perfil)