from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.viewsets import (
    avaliacao_viewset,
    carrinho_viewset,
    categoria_viewset,
    cupom_viewset,
    dicas_sustentaveis_viewset,
    doacao_viewset,
    faleconosco_viewset,
    item_pedido_viewset,
    login_viewset,
    notificacao_viewset,
    pacote_surpresa_viewset,
    pedido_viewset,
    perfil_viewset,
    produto_viewset,
    receita_viewset,
)

router = routers.DefaultRouter()
router.register(r"Perfil", perfil_viewset.PerfilViewSet)
router.register(r"receitas", receita_viewset.ReceitaViewSet)
router.register(r"pedido", pedido_viewset.PedidoViewSet, basename="pedido")
router.register(r"cupom", cupom_viewset.CupomViewSet)
router.register(
    r"itemPedido", item_pedido_viewset.ItemPedidoViewSet, basename="Item_pedido"
)
router.register(r"categoria", categoria_viewset.CategoriaViewSet)
router.register(r"doacao", doacao_viewset.DoacaoViewSet)
router.register(r"faleConosco", faleconosco_viewset.FaleConoscoViewSet)
router.register(r"produto", produto_viewset.ProdutoViewSet)
router.register(r"categoriasdicas", dicas_sustentaveis_viewset.CategoriaDicaViewSet)
router.register(r"dicas", dicas_sustentaveis_viewset.DicaViewSet)
router.register(
    r"notificacao", notificacao_viewset.NotificacaoViewSet, basename="notificacao"
)
router.register(r"avaliacoes", avaliacao_viewset.AvaliacaoViewSet)
router.register(r"pacotes-surpresa", pacote_surpresa_viewset.PacoteSurpresaViewSet)
router.register(r"auth", login_viewset.AuthViewSet, basename="auth")
router.register(r"carrinho", carrinho_viewset.CarrinhoViewSet, basename="carrinho")


urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", include("core.urls")),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api-auth/", include("rest_framework.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
