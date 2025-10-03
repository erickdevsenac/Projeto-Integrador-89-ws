from django.db import models
from django.utils import timezone
from django.urls import reverse

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Produto(models.Model):
    vendedor = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.CASCADE,
        related_name='produtos',
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
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
    
    codigo_produto = models.CharField(
        "Código do Produto (SKU)",
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Código de barras ou SKU. Deve ser único."
    )
    data_fabricacao = models.DateField("Data de Fabricação", blank=True, null=True)
    data_validade = models.DateField("Data de Validade", blank=True, null=True)
    
    quantidade_estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True) 

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    @property
    def disponivel_para_venda(self):
        return self.ativo and self.quantidade_estoque > 0

    def __str__(self):
       return f'{self.nome} | Vendedor: {self.vendedor.usuario.username}'


    def get_absolute_url(self):
        return reverse('core:produto_detalhe', kwargs={'pk': self.pk})
