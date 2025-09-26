from rest_framework import viewsets 
from core.models import Categoria
from core.serializers import CategoriaSerializer 

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer