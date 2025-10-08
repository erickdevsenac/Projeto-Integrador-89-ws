from rest_framework import serializers
from core.models import Produto
from .perfil_serializer import PerfilSerializer
from .categoria_serializer import CategoriaProdutoSerializer

class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializador para LISTAS de produtos."""
    vendedor = PerfilSerializer(read_only=True)
    categoria = CategoriaProdutoSerializer(read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'preco', 'imagem_principal', 'vendedor_nome', 'categoria_nome', 'disponivel_para_venda'
        ]

class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializador completo para a PÁGINA DE DETALHE de um produto."""
    vendedor = PerfilSerializer(read_only=True)
    categoria = CategoriaProdutoSerializer(read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'preco', 'preco_original', 'motivo_desconto',
            'imagem_principal', 'codigo_produto', 'data_validade', 'quantidade_estoque',
            'ativo', 'destaque', 'vendedor', 'categoria', 'disponivel_para_venda'
        ]