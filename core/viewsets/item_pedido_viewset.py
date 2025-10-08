from rest_framework import viewsets
from core.models import ItemPedido
from core.serializers import ItemPedidoSerializer

class ItemPedidoViewSet(viewsets.ModelViewSet):
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer