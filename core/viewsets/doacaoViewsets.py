from rest_framework import viewsets 
from core.models import Doacao
from core.serializers import DoacaoSerializer 

class DoacaoViewSet(viewsets.ModelViewSet):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
