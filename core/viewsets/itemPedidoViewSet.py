from rest_framework import viewsets
from models.item_pedido_model import ItemPedido
from..serializers import ItemPedidoSerializer

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    

   
