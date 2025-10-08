from rest_framework import serializers
from core.models.avaliacao import Avaliacao
from .usuarioSerializer import UserSerializer

class AvaliacaoSerializer(serializers.ModelSerializer):
    """Serializador para avaliações e comentários."""
    autor = UserSerializer(read_only=True)

    class Meta:
        model = Avaliacao
        fields = ('id', 'autor', 'nota', 'texto', 'data_criacao')