from rest_framework import viewsets
from ..models import Receita
from ..serializers import ReceitaSerializer

class ReceitaViewSet(viewsets.ModelViewSet):
    queryset = Receita.objects.all().order_by('id')
    serializer_class = ReceitaSerializer