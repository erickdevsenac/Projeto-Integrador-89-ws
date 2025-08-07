from django.contrib import admin
from core.models.perfil_model import Perfil
from core.models.produto_model import Produto, Categoria
from core.models.item_pedido_model import ItemPedido
from core.models.pedido_model import Pedido, PedidoVendedor
from core.models.doacoes_model import Doacao


# core/admin.py
from django.contrib import admin
# ... seus imports

# Melhora a visualização de Produtos no Admin
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'vendedor', 'preco', 'quantidade_estoque', 'ativo', 'disponivel_para_venda')
    list_filter = ('ativo', 'categoria', 'vendedor')
    search_fields = ('nome', 'descricao', 'vendedor__nome_negocio')

# Permite ver os itens do pedido dentro do próprio pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    # extra = 0 # Não mostra formulários de itens extras por padrão
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal') # Campos não editáveis

@admin.register(PedidoVendedor)
class PedidoVendedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido_principal', 'vendedor', 'status', 'valor_subtotal')
    list_filter = ('status', 'vendedor')
    inlines = [ItemPedidoInline] # Adiciona os itens na tela do sub-pedido

# Registra os outros modelos de forma simples
admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(Doacao)