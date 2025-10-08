import uuid
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.core.validators import MinValueValidator
from .time_stamp import TimeStampedModel

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'")

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class ProdutoManager(models.Manager):
    """Manager customizado para o modelo Produto"""
    
    def disponiveis(self):
        """Retorna apenas produtos disponíveis para venda (ativos e com estoque)"""
        return self.filter(ativo=True, quantidade_estoque__gt=0)
    
    def por_categoria(self, categoria_slug):
        """Filtra produtos disponíveis por slug de categoria"""
        return self.disponiveis().filter(categoria__slug=categoria_slug)
    
    def buscar(self, termo):
        """Busca produtos disponíveis por um termo de pesquisa"""
        return self.disponiveis().filter(
            Q(nome__icontains=termo) | 
            Q(descricao__icontains=termo) |
            Q(categoria__nome__icontains=termo)
        )

class Produto(TimeStampedModel):
    """
    Modelo para produtos individuais, com foco em sustentabilidade e controle de validade.
    """
    class MotivoDesconto(models.TextChoices):
        VALIDADE_PROXIMA = 'VALIDADE', 'Próximo da Validade'
        DEFEITO_ESTETICO = 'ESTETICA', 'Defeito Estético'
        EXCESSO_ESTOQUE = 'EXCESSO', 'Excesso de Estoque'

    vendedor = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.CASCADE,
        related_name='produtos',
        limit_choices_to={'tipo': 'VENDEDOR'}
    )
    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos' 
    )
    
    preco = models.DecimalField(
        "Preço de Venda",
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    preco_original = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preço original do produto, antes do desconto."
    )
    motivo_desconto = models.CharField(
        max_length=10, 
        choices=MotivoDesconto.choices, 
        blank=True, 
        null=True,
        help_text="O motivo pelo qual este produto está com desconto."
    )
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    imagem_principal = models.ImageField(upload_to='produtos/', blank=True, null=True)
    
    # --- Controle de Estoque e Identificação ---
    quantidade_estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=1, help_text="Quantidade mínima para alerta de estoque baixo")
    codigo_produto = models.CharField(
        "Código (SKU)",
        max_length=50,
        unique=True,
        blank=True,
        help_text="Código de barras ou SKU. Será gerado automaticamente se deixado em branco."
    )
    
    data_validade = models.DateField(
        "Data de Validade",
        blank=True,
        null=True,
        help_text="Importante para produtos perecíveis."
    )
    
    ativo = models.BooleanField(default=True, help_text="Desmarque para 'pausar' o anúncio do produto.")
    destaque = models.BooleanField(default=False, help_text="Marque para destacar o produto na página inicial.")
    visualizacoes = models.PositiveIntegerField(default=0, editable=False)
    
    objects = ProdutoManager()

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['ativo', 'quantidade_estoque']),
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['vendedor', 'ativo']),
        ]

    def __str__(self):
        return f'{self.nome} | {self.vendedor.nome_negocio or self.vendedor.usuario.username}'

    def get_absolute_url(self):
        return reverse('core:produto_detalhe', kwargs={'produto_id': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.codigo_produto:
            self.codigo_produto = f'PROD-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)
    
    @property
    def imagem(self):
        return self.imagem_principal
    
    @property
    def disponivel_para_venda(self):
        return self.ativo and self.quantidade_estoque > 0
    
    @property
    def estoque_baixo(self):
        return self.quantidade_estoque > 0 and self.quantidade_estoque <= self.estoque_minimo

class PacoteSurpresa(TimeStampedModel):
    vendedor = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'VENDEDOR'}
    )
    nome = models.CharField(max_length=100, default="Pacote Surpresa do Dia")
    descricao = models.TextField(help_text="Ex: Contém uma seleção de legumes e verduras do dia.")
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='pacotes/', blank=True, null=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pacote Surpresa"
        verbose_name_plural = "Pacotes Surpresa"

    def __str__(self):
        return f'{self.nome} - {self.vendedor.nome_negocio}'