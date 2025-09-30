from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers

from core.viewsets import doacaoViewsets, produtosview

router = routers.DefaultRouter()
router.register(r'doacao', doacaoViewsets.DoacaoViewSet)
router.register(r'users',ProdutoViewSet)

router.register(r'produtos', produtosview.ProdutoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('core.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


