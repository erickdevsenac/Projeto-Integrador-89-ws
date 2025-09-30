from rest_framework import viewsets
from core.models import Perfil
from core.serializers import PerfilSerializer

class PerfilViewSetv(viewsets.ModelViewSet):
    queryset= Perfil.objects.all()
    serializer_class = PerfilSerializer
