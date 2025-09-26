from rest_framework import viewsets, permissions
from core.models import Loja
from core.serializers import LojaSerializer

class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loja.objects.filter(user=self.request.user)
