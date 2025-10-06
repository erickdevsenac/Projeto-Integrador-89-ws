from rest_framework import serializers
from core.models import Perfil
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class PerfilSerializer(serializers.ModelSerializer):
    usuario = UserSerializer()  

    class Meta:
        model= Perfil
        fields= ['usuario','tipo','foto_perfil', 'nome_negocio', 'logo_ong', 'telefone', 'endereco', 'cnpj', 'descricao_parceiro']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')
        user = User.objects.create_user(**user_data)
        perfil = Perfil.objects.create(usuario=user, **validated_data)
        
        return perfil