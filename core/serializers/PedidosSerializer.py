from rest_framework import serializers
from ..models import Pedido

class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model= Pedido
        fields= ['id', 'cliente', 'produto', 'quantidade', 'status', 'data_criacao'] 




