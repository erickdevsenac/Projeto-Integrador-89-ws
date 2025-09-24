from rest_framework import serializers
from core.models import Categoria, Produto
from .perfilPublicoSerializer import PerfilPublicoSerializer

# --- Serializer Principal de Produto ---
class ProdutoSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField(read_only=True)
    vendedor = PerfilPublicoSerializer(read_only=True) 

    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset = Categoria.objects.all(), source='categoria', write_only=True, required=False
    )
    
    disponivel_para_venda = serializers.BooleanField(read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'imagem',
            'vendedor', 
            'categoria', 
            'categoria_id',
            'quantidade_estoque',
            'ativo',
            'disponivel_para_venda', 
            'codigo_produto',
            'data_fabricacao',
            'data_validade',
            'data_criacao',
        ]
        read_only_fields = ['vendedor', 'data_criacao'] 

    def create(self, validated_data):
        """
        Define o vendedor automaticamente como o usuário logado ao criar um produto.
        """
        perfil_vendedor = self.context['request'].user.perfil
        validated_data['vendedor'] = perfil_vendedor
        return super().create(validated_data)        
        