from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from core.viewsets import produtoViewset
from core.viewsets import dicas_sustentaveisViewset
from core.viewsets import notificacaoViewset
from core.viewsets import UsuarioViewSet
from core.viewsets import ItemPedidoViewSet
from core.viewsets import doacaoViewsets
from core.viewsets import categoriaViewset, vendedorViewset,cupomViewset,faleconoscoViewset
router = routers.DefaultRouter()
router.register(r'ItemPedido', ItemPedidoViewSet, basename="Item_pedido")
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

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


