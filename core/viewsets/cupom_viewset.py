from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from core.models.cupom import Cupom
from core.serializers.cupom_serializer import CupomSerializer

class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer
    permission_classes = [IsAdminUser]
    

    def get_queryset(self):
        return Cupom.objects.filter(ativo=True)
