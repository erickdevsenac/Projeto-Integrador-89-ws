from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from ..serializers import UserSerializer

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite que os Usuários sejam visualizados (APENAS POR ADMINS).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] 