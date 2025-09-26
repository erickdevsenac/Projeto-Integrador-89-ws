from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco','destaque')
    list_filter = ('destaques',)
    search_fields = ('nome')