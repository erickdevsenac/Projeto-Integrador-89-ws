from rest_framework import serializers
from models import ItemPedido

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = '__all__' 
