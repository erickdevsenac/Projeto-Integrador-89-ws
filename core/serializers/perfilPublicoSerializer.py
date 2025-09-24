from rest_framework import serializers
from core.models import Perfil

class PerfilPublicoSerializer(serializers.ModelSerializer):
    """
    Um serializer que expõe apenas informações públicas do perfil 
    (útil para mostrar informações do vendedor em um produto).
    """
    usuario = serializers.StringRelatedField(read_only=True) 

    class Meta:
        model = Perfil
        fields = ['usuario', 'tipo', 'foto_perfil', 'nome_negocio', 'descricao_parceiro']
