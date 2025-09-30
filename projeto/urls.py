from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from core.viewsets import (produtoViewset,
                           dicas_sustentaveisViewset,
                           notificacaoViewset,
                           UsuarioViewSet,
                           ItemPedidoViewSet,
                           doacaoViewsets,
                           categoriaViewset, 
                           vendedorViewset,
                           cupomViewset,
                           faleconoscoViewset,
                           avaliacaoViewset,
                           receitaViewset,
                           comentariosViewSet, 
                           pedidoViewset, 
                          )

router = routers.DefaultRouter()
router.register(r'Perfil', PerfilViewSet.PerfilViewSetv)
router.register(r'Pedido', PedidosViewSet.PedidosViewSetv)
router.register(r'Receita', ReceitasViewSet.ReceitasViewSetv)
router.register(r'receitas', receitaViewset.ReceitaViewSet)
router.register(r'comentarios', comentariosViewSet.ComentariosViewset)
router.register(r'pedido', pedidoViewset.PedidoViewSet, basename='Pedido') 
router.register(r'cupom', cupomViewset.CupomViewSet)
router.register(r'itemPedido', itemPedidoViewSet.ItemPedidoViewSet, basename="Item_pedido")
router.register(r'users', UsuarioViewSet, basename='usuario')
router.register(r'categoria', categoriaViewset.CategoriaViewSet)
router.register(r'vendedor', vendedorViewset.VendedorViewSet)
router.register(r'doacao', doacaoViewsets.DoacaoViewSet)
router.register(r'cupom',cupomViewset.CupomViewSet)
router.register(r'faleConosco',faleconoscoViewset.FaleConoscoViewSet)
router.register(r'produto',produtoViewset.ProdutoViewSet)
router.register(r'categoriasdicas',dicas_sustentaveisViewset.CategoriaDicaViewSet)
router.register(r'dicas',dicas_sustentaveisViewset.DicaViewSet)
router.register(r'notificacao', notificacaoViewset.NotificacaoViewSet)
router.register(r'avaliacoes', avaliacaoViewset.AvaliacaoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
