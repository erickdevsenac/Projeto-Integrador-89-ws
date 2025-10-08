from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.models import Receita
from core.serializers import ReceitaListSerializer, ReceitaDetailSerializer

class ReceitaViewSet(viewsets.ModelViewSet):
    queryset = Receita.objects.filter(disponivel=True)
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReceitaListSerializer
        return ReceitaDetailSerializer

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)