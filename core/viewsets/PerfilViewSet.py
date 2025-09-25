from rest_framework import viewsets
from core.models import Perfil
from core.serializers import PerfilSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    queryset= Perfil.objects.all()
    serializer_class = PerfilSerializer



