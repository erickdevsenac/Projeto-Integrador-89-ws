from rest_framework import serializers
from ..models import Perfil
from .produtoSerializer import ProdutoListSerializer

class VendedorSerializer(serializers.ModelSerializer):
    """ Serializador específico para o perfil de Vendedor, incluindo seus produtos. """
    produtos = ProdutoListSerializer(many=True, read_only=True)

    class Meta:
        model = Perfil
        fields = [
            'nome_negocio', 'foto_perfil', 'telefone', 'endereco', 'descricao_parceiro',
            'avaliacao_media', 'total_avaliacoes', 'verificado', 'produtos'
        ]