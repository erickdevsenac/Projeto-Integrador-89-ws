from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Receita
from ..serializers import ReceitasSerializer
 
class ReceitasViewSetv(viewsets.ModelViewSet):
    queryset= Receita.objects.all()
    serializer_class = ReceitasSerializer
    permission_classes = [IsAuthenticated]
 