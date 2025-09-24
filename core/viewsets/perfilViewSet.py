from rest_framework import permissions, viewsets
from core.models import Perfil
from core.serializers import (PerfilPublicoSerializer)

class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint da API que permite que perfis de vendedores e ONGs sejam visualizados.
    Usamos ReadOnlyModelViewSet para não permitir edição por aqui.
    """
    queryset = Perfil.objects.filter(tipo__in=[Perfil.TipoUsuario.VENDEDOR, Perfil.TipoUsuario.ONG])
    serializer_class = PerfilPublicoSerializer
    permission_classes = [permissions.AllowAny] 
