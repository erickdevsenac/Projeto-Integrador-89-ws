from rest_framework import viewsets
from ..models import FaleConosco
from ..serializers import FaleConoscoSerializer
 
class FaleConoscoViewSet(viewsets.ModelViewSet):
    queryset = FaleConosco.objects.all().order_by('-data_envio')
    serializer_class = FaleConoscoSerializer