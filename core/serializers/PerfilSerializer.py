-from rest_framework import serializers
from ..models import Perfil
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class PerfilSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()  # nested user data

    class Meta:
        model= Perfil
        fields= ['usuario','tipo','foto_perfil', 'nome_negocio', 'logo_ong', 'telefone', 'endereco', 'cnpj', 'descricao_parceiro']
