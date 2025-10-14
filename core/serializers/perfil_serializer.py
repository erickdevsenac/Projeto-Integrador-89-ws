from rest_framework import serializers

from ..models import Perfil
from .usuario_serializer import UserSerializer


class PerfilSerializer(serializers.ModelSerializer):
    """Serializador detalhado para o Perfil do usuário."""

    usuario = UserSerializer(read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Perfil
        fields = [
            "usuario",
            "tipo",
            "tipo_display",
            "foto_perfil",
            "nome_completo",
            "nome_negocio",
            "telefone",
            "endereco",
            "cnpj",
            "descricao_parceiro",
            "avaliacao_media",
            "total_avaliacoes",
            "verificado",
            "avaliacoes",
        ]
        read_only_fields = ("avaliacoes",)
