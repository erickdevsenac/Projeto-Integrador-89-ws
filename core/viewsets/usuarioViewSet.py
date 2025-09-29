from rest_framework import viewsets
from django.contrib.auth.models import User
from core.serializers import UsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite que os Usuarios sejam vizualizados ou editados
    """
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer