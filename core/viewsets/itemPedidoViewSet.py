from rest_framework import viewsets
from core.models.item_pedido_model import ItemPedido
from core.serializers.itemPedidoSerializers import ItemPedidoSerializer

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    

   
