from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from core.viewsets import (produtoViewset,
                           dicas_sustentaveisViewset,
                           notificacaoViewset,
                           doacaoViewsets,
                           categoriaViewset, 
                           vendedorViewset,
                           cupomViewset,
                           faleconoscoViewset,
                           avaliacaoViewset,
                           comentariosViewSet, 
                           pedidoViewset, 
                           itemPedidoViewSet,
                           perfilViewSet,
                           cadastro_produtoViewset,
                           receitaViewset,
                           usuarioViewSet
                          )

router = routers.DefaultRouter()
router.register(r'Perfil', perfilViewSet.PerfilViewSet)
router.register(r'Pedido', pedidoViewset.PedidoViewSet)
router.register(r'receitas', receitaViewset.ReceitaViewSet)
router.register(r'comentarios', comentariosViewSet.ComentariosViewset)
router.register(r'pedido', pedidoViewset.PedidoViewSet, basename='Pedido') 
router.register(r'cupom', cupomViewset.CupomViewSet)
router.register(r'itemPedido', itemPedidoViewSet.ItemPedidoViewSet, basename="Item_pedido")
router.register(r'users', usuarioViewSet.UsuarioViewSet, basename='usuario')
router.register(r'categoria', categoriaViewset.CategoriaViewSet)
router.register(r'vendedor', vendedorViewset.VendedorViewSet)
router.register(r'doacao', doacaoViewsets.DoacaoViewSet)
router.register(r'faleConosco', faleconoscoViewset.FaleConoscoViewSet)
router.register(r'produto', produtoViewset.ProdutoViewSet)
router.register(r'categoriasdicas', dicas_sustentaveisViewset.CategoriaDicaViewSet)
router.register(r'dicas', dicas_sustentaveisViewset.DicaViewSet)
router.register(r'notificacao', notificacaoViewset.NotificacaoViewSet)
router.register(r'avaliacoes', avaliacaoViewset.AvaliacaoViewSet)
router.register(r'cadastro_produto',cadastro_produtoViewset.CadastroProdutoViewSet )

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token-auth/', obtain_auth_token),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
