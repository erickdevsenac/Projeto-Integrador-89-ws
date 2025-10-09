# core/admin.py
from django.contrib import admin
from core.models.avaliacao_model import Avaliacao
from core.models.doacoes_model import Doacao
from core.models.equipe_models import EquipeDev
from core.models.item_pedido_model import ItemPedido
from core.models.pedido_model import Pedido, PedidoVendedor
from core.models.perfil_model import Perfil
from core.models.produto_model import Categoria, Produto
from core.models.receita_model import Receita
from core.models.comentarios import Comentario
from core.models.cupom_model import Cupom
from core.models.notificacao_model import Notificacao
from core.models.fale_conosco_model import FaleConosco
from core.models.dicas_sustentaveis import Dica,CategoriaDica

# ... seus imports


# Melhora a visualização de Produtos no Admin
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "vendedor",
        "preco",
        "quantidade_estoque",
        "ativo",
        "disponivel_para_venda",
    )
    list_filter = ("ativo", "categoria", "vendedor")
    search_fields = ("nome", "descricao", "vendedor__nome_negocio")


# Permite ver os itens do pedido dentro do próprio pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    # extra = 0 # Não mostra formulários de itens extras por padrão
    readonly_fields = (
        "produto",
        "quantidade",
        "preco_unitario",
        "subtotal",
    )  # Campos não editáveis


@admin.register(PedidoVendedor)
class PedidoVendedorAdmin(admin.ModelAdmin):
    list_display = ("id", "pedido_principal", "vendedor", "status", "valor_subtotal")
    list_filter = ("status", "vendedor")
    inlines = [ItemPedidoInline]  # Adiciona os itens na tela do sub-pedido


# Registra os outros modelos de forma simples
admin.site.register(Perfil)
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(Doacao)
admin.site.register(Receita)
admin.site.register(EquipeDev)
admin.site.register(Avaliacao)
admin.site.register(Comentario)
admin.site.register(Cupom)
admin.site.register(Notificacao)
admin.site.register(FaleConosco)
admin.site.register(Dica)
admin.site.register(CategoriaDica)

# Lista os Pedidos
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
