from django.db import models
from django.urls import reverse
from .time_stamp_model import TimeStampedModel

class Categoria(TimeStampedModel):
    """Modelo para categorias de produtos"""
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'"
    )
    descricao = models.TextField(blank=True, help_text="Descrição da categoria")
    imagem = models.ImageField(
        upload_to='categorias/', 
        blank=True, 
        null=True,
        help_text="Imagem representativa da categoria"
    )
    ativa = models.BooleanField(default=True, help_text="Categoria ativa no sistema")
    ordem = models.PositiveIntegerField(
        default=0, 
        help_text="Ordem de exibição (menor número aparece primeiro)"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse('core:produtos') + f'?categoria={self.slug}'
    
    @property
    def produtos_ativos_count(self):
        """Retorna a quantidade de produtos ativos na categoria"""
        return self.produtos.filter(ativo=True, quantidade_estoque__gt=0).count()