from rest_framework import viewsets
from core.models.fale_conosco import FaleConosco
from core.serializers.faleconosco_serializer import FaleConoscoSerializer
 
class FaleConoscoViewSet(viewsets.ModelViewSet):
    queryset = FaleConosco.objects.all().order_by('-data_envio')
    serializer_class = FaleConoscoSerializer