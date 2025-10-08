from rest_framework import serializers
from ..models import CategoriaProduto

class CategoriaProdutoSerializer(serializers.ModelSerializer):
    """Serializador para Categorias de Produto."""
    produtos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CategoriaProduto
        fields = ['id', 'nome', 'slug', 'produtos_count']