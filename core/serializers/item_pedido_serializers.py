from rest_framework import serializers
from ..models import ItemPedido
from .produto_serializer import ProdutoListSerializer

class ItemPedidoSerializer(serializers.ModelSerializer):
    """Serializador para os itens dentro de um pedido."""
    produto = ProdutoListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'quantidade', 'preco_unitario', 'subtotal']