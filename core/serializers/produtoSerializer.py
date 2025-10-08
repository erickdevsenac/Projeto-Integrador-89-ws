from rest_framework import serializers
from ..models import Produto
from .PerfilSerializer import PerfilSerializer
from .categoriaSerializer import CategoriaProdutoSerializer

class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializador otimizado para LISTAS de produtos."""
    vendedor_nome = serializers.CharField(source='vendedor.nome_negocio', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

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