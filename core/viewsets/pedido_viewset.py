from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Pedido
from core.serializers import PedidoSerializer, pedido_serializer

class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para os Pedidos. Um cliente só pode ver e gerenciar seus próprios pedidos.
    """
    queryset = Pedido.objects.all()  # 👈 Adicione esta linha
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pedido.objects.filter(cliente=self.request.user.perfil)

    def get_serializer_class(self):
        if self.action == 'list':
            return pedido_serializer.PedidoListSerializer
        return PedidoSerializer

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user.perfil)
