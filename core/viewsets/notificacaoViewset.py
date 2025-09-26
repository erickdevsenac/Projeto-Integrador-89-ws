from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# Corrigindo: Se o modelo se chama 'Notificacao' no models.py, 
# a importação no Python deve usar o nome da classe.
from ..models import Notificacao 
from ..serializers import NotificacaoSerializer

class NotificacaoViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch'] 

    # 🔑 CORREÇÃO CRÍTICA: Adicionar a propriedade queryset
    # Isso resolve o erro do Router e define a base para o ViewSet.
    queryset = Notificacao.objects.all()


    def get_queryset(self):
        # Este método sobrescreve o queryset base, garantindo que
        # cada usuário só veja suas próprias notificações.
        return Notificacao.objects.filter(usuario=self.request.user)


    @action(detail=True, methods=['patch'])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        return Response({'status': 'Notificação marcada como lida'})
    
    # ... (O método nao_lidas está correto e não precisa de alteração)
    @action(detail=False, methods=['get'])
    def nao_lidas(self, request):
        count = self.get_queryset().filter(lida=False).count()
        return Response({'count': count})