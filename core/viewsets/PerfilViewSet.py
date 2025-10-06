from rest_framework import viewsets
from core.models import Perfil
from core.serializers import PerfilSerializer
from core.models import Perfil
from core.serializers import PerfilSerializer

class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet apenas de leitura (GET list e retrieve) para perfis.
    """
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
