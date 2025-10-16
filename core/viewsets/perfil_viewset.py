from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Perfil
from core.serializers import PerfilSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar Perfis.
    Um usuário só pode editar seu próprio perfil.
    """
    queryset = Perfil.objects.filter(ativo=True)
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Perfil.objects.all()
        return Perfil.objects.filter(ativo=True)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """ Rota customizada para o usuário ver e editar seu próprio perfil. """
        perfil = request.user.perfil
        if request.method == 'GET':
            serializer = self.get_serializer(perfil)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(perfil, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)