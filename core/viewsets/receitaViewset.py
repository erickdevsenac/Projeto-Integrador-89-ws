from rest_framework import viewsets
from core.models import Receita
from core.serializers import ReceitaSerializer

class ReceitaViewSet(viewsets.ModelViewSet):
    queryset = Receita.objects.all().order_by('id')
    serializer_class = ReceitaSerializer