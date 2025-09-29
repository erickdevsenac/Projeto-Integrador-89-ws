from rest_framework import serializers
from core.models import Loja, ProdutoVendedor, EstatisticaVenda

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoVendedor
        fields = ['id', 'nome', 'descricao', 'preco', 'imagem']

class EstatisticaVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatisticaVenda
        fields = ['total_vendas', 'receita_total']

class LojaSerializer(serializers.ModelSerializer):
    produtos = ProdutoSerializer(many=True, read_only=True)
    estatisticas = EstatisticaVendaSerializer(read_only=True)

    class Meta:
        model = Loja
        fields = ['id', 'nome', 'imagem', 'localizacao', 'produtos', 'estatisticas']
