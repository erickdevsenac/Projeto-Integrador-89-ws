from rest_framework import permissions, viewsets

from core.models.produto import PacoteSurpresa
from core.serializers.pacote_surpresa_serializer import PacoteSurpresaSerializer


class PacoteSurpresaViewSet(viewsets.ModelViewSet):
    queryset = PacoteSurpresa.objects.all().order_by("-data_criacao")
    serializer_class = PacoteSurpresaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filtra pacotes surpresa para mostrar apenas os ativos e disponíveis para usuários não autenticados."""
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return queryset  # Admins podem ver todos os pacotes
        return queryset.filter(ativo=True, quantidade_estoque__gt=0)

    def perform_create(self, serializer):
        serializer.save(
            vendedor=self.request.user.perfil
        )  # Associa o pacote ao perfil do vendedor logado
