from rest_framework import viewsets
from core.models import Comentario
from core.serializers import ComentariosSerializer
 
class ComentariosViewset(viewsets.ModelViewSet):
    queryset = Comentario.objects.all().order_by('id')
    serializer_class = ComentariosSerializer