from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from core.viewsets import(avaliacao_viewset, categoria_viewset, cupom_viewset, dicas_sustentaveis_viewset, doacao_viewset, faleconosco_viewset, item_pedido_viewset, notificacao_viewset, pedido_viewset, produto_viewset, perfil_viewset,
                           receita_viewset
                          )

router = routers.DefaultRouter()
router.register(r'Perfil', perfil_viewset.PerfilViewSet)
router.register(r'receitas', receita_viewset.ReceitaViewSet)
router.register(r'pedido', pedido_viewset.PedidoViewSet, basename='pedido')
router.register(r'cupom', cupom_viewset.CupomViewSet)
router.register(r'itemPedido', item_pedido_viewset.ItemPedidoViewSet, basename="Item_pedido")
router.register(r'categoria', categoria_viewset.CategoriaViewSet)
router.register(r'doacao', doacao_viewset.DoacaoViewSet)
router.register(r'faleConosco', faleconosco_viewset.FaleConoscoViewSet)
router.register(r'produto', produto_viewset.ProdutoViewSet)
router.register(r'categoriasdicas', dicas_sustentaveis_viewset.CategoriaDicaViewSet)
router.register(r'dicas', dicas_sustentaveis_viewset.DicaViewSet)
router.register(r'notificacao', notificacao_viewset.NotificacaoViewSet, basename='notificacao')
router.register(r'avaliacoes', avaliacao_viewset.AvaliacaoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
