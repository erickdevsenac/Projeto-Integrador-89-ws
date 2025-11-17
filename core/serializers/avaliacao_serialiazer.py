from rest_framework import serializers

from core.models.avaliacao import Avaliacao

from .usuario_serializer import UserSerializer


class AvaliacaoSerializer(serializers.ModelSerializer):
    """Serializador para avaliações e comentários."""

    autor = UserSerializer(read_only=True)

    class Meta:
        model = Avaliacao
        fields = (
            "id",
            "autor",
            "nota",
            "texto",
            "data_criacao",
            "content_type",
            "object_id",  # Adicione os campos aqui
        )
        extra_kwargs = {
            "content_type": {"write_only": True},
            "object_id": {"write_only": True},
        }
