# core/serializers/melhorados.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import (
    Perfil, Produto, Categoria, Pedido, PedidoVendedor, 
    ItemPedido, Cupom, Receita
)


class UserSerializer(serializers.ModelSerializer):
    """Serializador para o modelo User do Django"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class PerfilSerializer(serializers.ModelSerializer):
    """Serializador melhorado para o modelo Perfil"""
    usuario = UserSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Perfil
        fields = [
            'usuario', 'tipo', 'tipo_display', 'foto_perfil', 'nome_negocio',
            'telefone', 'endereco', 'cnpj', 'descricao_parceiro',
            'logo_ong', 'imagem_carrossel1', 'imagem_carrossel2', 
            'imagem_carrossel3', 'objetivo'
        ]
        read_only_fields = ['usuario']

    def validate_cnpj(self, value):
        """Validação básica de CNPJ"""
        if value and self.instance:
            # Remove caracteres não numéricos
            cnpj_limpo = ''.join(filter(str.isdigit, value))
            if len(cnpj_limpo) != 14:
                raise serializers.ValidationError("CNPJ deve ter 14 dígitos.")
        return value


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializador para categorias de produtos"""
    produtos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'produtos_count']
    
    def get_produtos_count(self, obj):
        """Retorna a quantidade de produtos ativos na categoria"""
        return obj.produtos.filter(ativo=True, quantidade_estoque__gt=0).count()


class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializador otimizado para listagem de produtos"""
    vendedor_nome = serializers.CharField(source='vendedor.nome_negocio', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    disponivel_para_venda = serializers.ReadOnlyField()
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'preco', 'imagem', 'vendedor_nome',
            'categoria_nome', 'disponivel_para_venda', 'data_criacao'
        ]


class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializador detalhado para produtos individuais"""
    vendedor = PerfilSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    disponivel_para_venda = serializers.ReadOnlyField()
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'preco', 'imagem', 'codigo_produto',
            'data_fabricacao', 'data_validade', 'quantidade_estoque',
            'ativo', 'data_criacao', 'vendedor', 'categoria',
            'disponivel_para_venda'
        ]
        read_only_fields = ['id', 'data_criacao', 'vendedor']


class ProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para criação e atualização de produtos"""
    
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'preco', 'imagem', 'codigo_produto',
            'data_fabricacao', 'data_validade', 'quantidade_estoque',
            'ativo', 'categoria'
        ]
    
    def validate_preco(self, value):
        """Validação do preço"""
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser maior que zero.")
        return value
    
    def validate_quantidade_estoque(self, value):
        """Validação do estoque"""
        if value < 0:
            raise serializers.ValidationError("A quantidade em estoque não pode ser negativa.")
        return value


class ItemPedidoSerializer(serializers.ModelSerializer):
    """Serializador para itens do pedido"""
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    produto_imagem = serializers.ImageField(source='produto.imagem', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemPedido
        fields = [
            'id', 'produto', 'produto_nome', 'produto_imagem',
            'quantidade', 'preco_unitario', 'subtotal'
        ]
    
    def get_subtotal(self, obj):
        """Calcula o subtotal do item"""
        return obj.subtotal()


class PedidoVendedorSerializer(serializers.ModelSerializer):
    """Serializador para sub-pedidos dos vendedores"""
    vendedor_nome = serializers.CharField(source='vendedor.nome_negocio', read_only=True)
    itens = ItemPedidoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PedidoVendedor
        fields = [
            'id', 'vendedor', 'vendedor_nome', 'status', 'status_display',
            'valor_subtotal', 'itens'
        ]


class PedidoSerializer(serializers.ModelSerializer):
    """Serializador para pedidos principais"""
    cliente_nome = serializers.CharField(source='cliente.usuario.get_full_name', read_only=True)
    sub_pedidos = PedidoVendedorSerializer(many=True, read_only=True)
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    status_pagamento_display = serializers.CharField(source='get_status_pagamento_display', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'cliente_nome', 'valor_total', 'data_pedido',
            'endereco_entrega', 'forma_pagamento', 'forma_pagamento_display',
            'status_pagamento', 'status_pagamento_display', 'sub_pedidos'
        ]
        read_only_fields = ['id', 'data_pedido', 'cliente']


class CupomSerializer(serializers.ModelSerializer):
    """Serializador para cupons de desconto"""
    tipo_desconto_display = serializers.CharField(source='get_tipo_desconto_display', read_only=True)
    usos_restantes = serializers.SerializerMethodField()
    
    class Meta:
        model = Cupom
        fields = [
            'id', 'codigo', 'tipo_desconto', 'tipo_desconto_display',
            'valor_desconto', 'data_validade', 'ativo', 'usos_realizados',
            'limite_uso', 'usos_restantes', 'valor_minimo_compra'
        ]
    
    def get_usos_restantes(self, obj):
        """Calcula quantos usos restam para o cupom"""
        return max(0, obj.limite_uso - obj.usos_realizados)


class ReceitaSerializer(serializers.ModelSerializer):
    """Serializador para receitas"""
    autor_nome = serializers.CharField(source='autor.usuario.get_full_name', read_only=True)
    
    class Meta:
        model = Receita
        fields = [
            'id', 'titulo', 'descricao', 'imagem', 'tempo_preparo',
            'porcoes', 'autor', 'autor_nome', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao', 'autor']


# Serializadores para carrinho (usando sessão)
class CarrinhoItemSerializer(serializers.Serializer):
    """Serializador para itens do carrinho na sessão"""
    produto_id = serializers.IntegerField()
    nome = serializers.CharField(max_length=100)
    preco = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantidade = serializers.IntegerField(min_value=1)
    imagem = serializers.URLField(required=False, allow_blank=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


class CarrinhoSerializer(serializers.Serializer):
    """Serializador para o carrinho completo"""
    itens = CarrinhoItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantidade_total = serializers.IntegerField(read_only=True)