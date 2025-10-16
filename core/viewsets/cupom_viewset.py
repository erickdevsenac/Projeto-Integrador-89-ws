from rest_framework import viewsets
from core.models.cupom import Cupom
from core.serializers.cupom_serializer import CupomSerializer

class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer

    def get_queryset(self):
        return Cupom.objects.filter(ativo=True)
