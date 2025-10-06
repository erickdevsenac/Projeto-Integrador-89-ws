from rest_framework import viewsets, permissions
from core.models.avaliacao_model import Avaliacao
from core.serializers.avaliacaoSerialiazer import AvaliacaoSerializer

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all().order_by('-data_avaliacao')
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)