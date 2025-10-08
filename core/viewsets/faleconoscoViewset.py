from rest_framework import viewsets
from core.models.fale_conosco import FaleConosco
from core.serializers.faleconoscoSerializer import FaleConoscoSerializer
 
class FaleConoscoViewSet(viewsets.ModelViewSet):
    queryset = FaleConosco.objects.all().order_by('-data_envio')
    serializer_class = FaleConoscoSerializer