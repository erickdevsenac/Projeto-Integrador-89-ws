from rest_framework import viewsets
from core.models.pedido_model import Pedido
from core.serializers.pedidoserializers import PedidoSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-data_pedido')
    serializer_class = PedidoSerializer