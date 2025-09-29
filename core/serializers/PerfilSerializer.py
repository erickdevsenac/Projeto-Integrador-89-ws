from rest_framework import serializers
from core.models.perfil_model import Perfil

class PerfilSerializer(serializers.ModelSerializer):
    class meta:
        model= Perfil
        fields= ['Cliente','Vendedor','ONG']

