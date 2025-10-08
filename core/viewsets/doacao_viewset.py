from rest_framework import viewsets 
from core.models.doacoes import Doacao
from core.serializers import DoacaoSerializer 

class DoacaoViewSet(viewsets.ModelViewSet):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
