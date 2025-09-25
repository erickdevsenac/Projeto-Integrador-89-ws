from django.db import models
from django.db.models import Q

class ProdutoManager(models.Manager):
    """Manager customizado para produtos"""
    
    def disponiveis(self):
        """Retorna apenas produtos disponíveis para venda"""
        return self.filter(ativo=True, quantidade_estoque__gt=0)
    
    def por_categoria(self, categoria_slug):
        """Filtra produtos por categoria"""
        return self.filter(categoria__slug=categoria_slug)
    
    def buscar(self, termo):
        """Busca produtos por termo"""
        return self.filter(
            Q(nome__icontains=termo) | 
            Q(descricao__icontains=termo) |
            Q(categoria__nome__icontains=termo)
        )