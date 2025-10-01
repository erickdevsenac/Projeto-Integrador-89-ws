from rest_framework import serializers
from core.models import Comentario
 
class ComentariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['titulo','perfil','avaliaçao']