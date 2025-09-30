from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Notificacao 
from core.serializers import NotificacaoSerializer

class NotificacaoViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch'] 
    queryset = Notificacao.objects.all()


    def get_queryset(self):
        return Notificacao.objects.filter(usuario=self.request.user)


    @action(detail=True, methods=['patch'])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        return Response({'status': 'Notificação marcada como lida'})
    
    @action(detail=False, methods=['get'])
    def nao_lidas(self, request):
        count = self.get_queryset().filter(lida=False).count()
        return Response({'count': count})