from rest_framework import serializers

from core.models import EtapaPreparo, Ingrediente, Receita
from core.serializers.avaliacao_serialiazer import AvaliacaoSerializer

from .usuario_serializer import UserSerializer


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ["nome", "quantidade"]


class EtapaPreparoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtapaPreparo
        fields = ["ordem", "descricao"]


class ReceitaDetailSerializer(serializers.ModelSerializer):
    """Serializador detalhado para uma receita, incluindo ingredientes e etapas."""

    categoria = serializers.StringRelatedField()
    autor = UserSerializer(read_only=True)
    ingredientes = IngredienteSerializer(many=True, read_only=True)
    etapas = EtapaPreparoSerializer(many=True, read_only=True)

    class Meta:
        model = Receita
        fields = [
            "id",
            "nome",
            "descricao",
            "tempo_preparo",
            "rendimento",
            "imagem",
            "categoria",
            "autor",
            "ingredientes",
            "etapas",
            "avaliacoes",
        ]
        read_only_fields = ("avaliacoes",)


class ReceitaListSerializer(serializers.ModelSerializer):
    """
    Serializador para listas de receitas.
    """

    categoria = serializers.StringRelatedField()
    autor = UserSerializer(read_only=True)

    class Meta:
        model = Receita
        fields = [
            "id",
            "nome",
            "tempo_preparo",
            "rendimento",
            "imagem",
            "categoria",
            "autor",
        ]
