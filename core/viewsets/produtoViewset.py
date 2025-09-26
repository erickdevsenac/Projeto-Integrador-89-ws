from rest_framework import viewsets
from core.serializers.produtoSerializer import ProdutoSerializer
from core.models.produto_model import Produto

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset =Produto.objects.all()  
    serializer_class =ProdutoSerializer

