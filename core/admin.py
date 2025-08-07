from django.contrib import admin
from core.models.perfil_model import Perfil
from core.models.produto_model import Produto, Categoria
from core.models.item_pedido_model import ItemPedido
from core.models.pedido_model import Pedido, PedidoVendedor
from core.models.doacoes_model import Doacao


admin.site.register(Perfil)
admin.site.register(Produto)
admin.site.register(Categoria)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(PedidoVendedor)
admin.site.register(Doacao)

