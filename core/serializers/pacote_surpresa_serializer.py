from rest_framework import serializers

from core.models.produto import PacoteSurpresa

from .perfil_serializer import PerfilSerializer
from .produto_serializer import ProdutoListSerializer


class PacoteSurpresaSerializer(serializers.ModelSerializer):
    vendedor = PerfilSerializer(read_only=True)
    produtos_possiveis = ProdutoListSerializer(many=True, read_only=True)

    class Meta:
        model = PacoteSurpresa
        fields = [
            "id",
            "vendedor",
            "nome",
            "descricao",
            "preco",
            "imagem",
            "quantidade_estoque",
            "ativo",
            "tipo_conteudo",
            "instrucoes_especiais",
            "data_disponibilidade_inicio",
            "data_disponibilidade_fim",
            "produtos_possiveis",
            "esta_disponivel_agora",
        ]
        read_only_fields = ("esta_disponivel_agora",)
