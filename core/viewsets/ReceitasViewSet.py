from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Receita
from core.serializers import ReceitasSerializer
 
class ReceitasViewSet(viewsets.ModelViewSet):
    queryset= Receita.objects.all()
    serializer_class = ReceitasSerializer
    permission_classes = [IsAuthenticated]
 