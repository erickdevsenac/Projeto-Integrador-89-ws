from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Pedido
from core.serializers import pedidoserializer

class PedidosViewSetv(viewsets.ModelViewSet):
    queryset= Pedido.objects.all()
    serializer_class = pedidoserializer
    permission_classes = [IsAuthenticated]
