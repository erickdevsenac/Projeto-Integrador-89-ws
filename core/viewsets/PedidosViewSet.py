from rest_framework import viewsets
from ..models import Pedido
from ..serializers import PedidosSerializer

class PedidosViewSetv(viewsets.ModelViewSet):
    queryset= Pedido.objects.all()
    serializer_class = PedidosSerializer
