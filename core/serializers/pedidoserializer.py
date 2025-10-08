from rest_framework import serializers
from ..models import Pedido, PedidoVendedor
from .PerfilSerializer import PerfilSerializer
from .itemPedidoSerializers import ItemPedidoSerializer

class PedidoVendedorSerializer(serializers.ModelSerializer):
    """Serializador para o sub-pedido de um vendedor."""
    vendedor = PerfilSerializer(read_only=True)
    itens = ItemPedidoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PedidoVendedor
        fields = ['id', 'vendedor', 'status', 'status_display', 'valor_subtotal', 'itens']


class PedidoSerializer(serializers.ModelSerializer):
    """Serializador para o pedido principal do cliente (visão detalhada)."""
    cliente = PerfilSerializer(read_only=True)
    sub_pedidos = PedidoVendedorSerializer(many=True, read_only=True)
    status_pagamento_display = serializers.CharField(source='get_status_pagamento_display', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'cliente', 'valor_total', 'data_criacao',
            'endereco_entrega', 'forma_pagamento', 'status_pagamento',
            'status_pagamento_display', 'sub_pedidos'
        ]
        
class PedidoListSerializer(serializers.ModelSerializer):
    """
    Serializador para listas de pedidos (visão simplificada).
    """
    cliente_nome = serializers.CharField(source='cliente.nome_completo', read_only=True, default='')

    class Meta:
        model = Pedido
        fields = [
            'id',
            'numero_pedido',
            'cliente_nome',
            'valor_total',
            'status_pagamento',
            'data_criacao'
        ]