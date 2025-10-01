from rest_framework import serializers
from core.models.perfil_model import Perfil

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model= Perfil
        fields= ['usuario','tipo','foto_perfil', 'nome_negocio', 'logo_ong', 'telefone', 'endereco', 'cnpj', 'descricao_parceiro']
