from rest_framework import serializers
from ..models import Perfil

class PerfilSerializer(serializers.ModelSerializer):
    class meta:
        model= Perfil
        fields= ['Cliente','Vendedor','ONG']

