from django.contrib import admin
from core.models.models_usuarios import Perfil
from core.models.produto_models import Produto, Categoria

admin.site.register(Perfil)
admin.site.register(Produto)
admin.site.register(Categoria)
# admin.site.register(Fornecedor)
# admin.site.register(AdminSistema)

