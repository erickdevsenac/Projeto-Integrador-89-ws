from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    # O relacionamento mais importante para um marketplace: Quem vende o produto?
    vendedor = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.CASCADE,
        related_name='produtos',
        limit_choices_to={'tipo': 'VENDEDOR'}
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL, # Se a categoria for deletada, o produto não será.
        null=True,
        blank=True,
        related_name='produtos'
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    imagem = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        help_text="Imagem de apresentação do produto"
    )
    
    quantidade_estoque = models.PositiveIntegerField(
        default=0,
        help_text="Quantidade total que o vendedor tem disponível."
    )
    
    ativo = models.BooleanField(
        default=True,
        help_text="O vendedor pode desmarcar para 'pausar' o anúncio do produto."
    )
    
    data_criacao = models.DateTimeField(default=timezone.now)

    # Propriedade para verificar a disponibilidade real (ativo e com estoque)
    @property
    def disponivel_para_venda(self):
        return self.ativo and self.quantidade_estoque > 0

    def __str__(self):
        return f'{self.nome} | Vendedor: {self.vendedor.nome_negocio}'