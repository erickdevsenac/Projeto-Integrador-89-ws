from rest_framework import viewsets
from core.serializers import CupomSerializer
from core.models.cupom_model import Cupom

class CupomViewSet(viewsets.ModelViewSet):
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer
    