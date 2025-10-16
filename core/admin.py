from django.contrib import admin

from .models import (
    Avaliacao,
    CategoriaDica,
    CategoriaProduto,
    Cupom,
    Dica,
    Doacao,
    EquipeDev,
    FaleConosco,
    ItemPedido,
    Notificacao,
    PacoteSurpresa,
    Pedido,
    PedidoVendedor,
    Perfil,
    Produto,
    Receita,
)


class ItemPedidoInline(admin.TabularInline):
    """Permite visualizar os itens de um PedidoVendedor diretamente em sua página."""

    model = ItemPedido
    extra = 0
    readonly_fields = ("produto", "quantidade", "preco_unitario", "subtotal")

    def subtotal(self, obj):
        return obj.subtotal

    subtotal.short_description = "Subtotal"


class PedidoVendedorInline(admin.TabularInline):
    """Permite visualizar os Pedidos de Vendedores (sub-pedidos) dentro de um Pedido principal."""

    model = PedidoVendedor
    extra = 0
    readonly_fields = ("vendedor", "status", "valor_subtotal")
    show_change_link = True


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "get_full_name", "tipo", "nome_negocio")
    list_filter = ("tipo",)
    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "nome_negocio",
    )

    @admin.display(description="Nome Completo", ordering="usuario__first_name")
    def get_full_name(self, obj):
        full_name = obj.usuario.get_full_name()
        return full_name if full_name else obj.usuario.username


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "vendedor", "preco", "quantidade_estoque", "ativo")
    list_filter = ("ativo", "categoria", "vendedor")
    search_fields = ("nome", "descricao", "vendedor__nome_negocio")
    list_editable = ("preco", "quantidade_estoque", "ativo")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_pedido",
        "cliente",
        "valor_total",
        "status_pagamento",
        "data_criacao",
    )
    list_filter = ("status_pagamento", "data_criacao")
    search_fields = ("cliente__usuario__username", "numero_pedido")
    readonly_fields = ("cliente", "valor_total", "data_criacao", "numero_pedido")
    inlines = [PedidoVendedorInline]


@admin.register(PedidoVendedor)
class PedidoVendedorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_pedido_principal_id",
        "vendedor",
        "status",
        "valor_subtotal",
        "data_pedido",
    )
    list_filter = ("status", "vendedor")
    search_fields = ("vendedor__nome_negocio", "pedido_principal__numero_pedido")
    inlines = [ItemPedidoInline]

    @admin.display(
        description="Pedido Principal", ordering="pedido_principal__numero_pedido"
    )
    def get_pedido_principal_id(self, obj):
        return obj.pedido_principal.numero_pedido

    @admin.display(
        description="Data do Pedido", ordering="pedido_principal__data_criacao"
    )
    def data_pedido(self, obj):
        return obj.pedido_principal.data_criacao


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "tipo_desconto",
        "valor_desconto",
        "ativo",
        "data_validade",
    )
    list_filter = ("ativo", "tipo_desconto")
    search_fields = ("codigo",)


admin.site.register(CategoriaProduto)
admin.site.register(Doacao)
admin.site.register(Receita)
admin.site.register(EquipeDev)
admin.site.register(Avaliacao)
admin.site.register(Notificacao)
admin.site.register(FaleConosco)
admin.site.register(Dica)
admin.site.register(CategoriaDica)
admin.site.register(PacoteSurpresa)
