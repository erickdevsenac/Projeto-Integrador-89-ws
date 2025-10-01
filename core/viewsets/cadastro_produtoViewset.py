# Seu_app/views.py

from rest_framework import viewsets
from core.models.cadastroprodutos_model import Cadastro_Produto
from core.serializers.cadastroprodutoSerializer import CadastroProdutoSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class CadastroProdutoViewSet(viewsets.ModelViewSet):
    queryset = Cadastro_Produto.objects.all()
    serializer_class = CadastroProdutoSerializer