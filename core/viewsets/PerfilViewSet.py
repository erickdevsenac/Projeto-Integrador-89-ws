from rest_framework import viewsets
from core.models import Perfil
from core.serializers import PerfilSerializer
from rest_framework.permissions import AllowAny

class PerfilViewSet(viewsets.ModelViewSet):

    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [AllowAny]