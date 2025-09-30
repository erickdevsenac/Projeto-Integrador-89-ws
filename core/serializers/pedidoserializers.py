from rest_framework import serializers
from core.models.pedido_model import Pedido

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['endereco_entrega', 'status_pagamento', 'forma_pagamento', 'data_pedido' ,'cliente', 'valor_total']