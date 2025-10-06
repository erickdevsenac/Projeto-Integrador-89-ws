from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

from .time_stamp_model import TimeStampedModel
from .categoria_model import Categoria
from .produto_manager import ProdutoManager

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


class Produto(models.Model):


class Produto(TimeStampedModel):
    """Modelo melhorado para produtos"""
    
    # Relacionamentos
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
    
    # Informações básicas
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Imagens
    imagem_principal = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        help_text="Imagem principal do produto"
    )
    imagem_2 = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        help_text="Segunda imagem do produto"
    )
    imagem_3 = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        help_text="Terceira imagem do produto"
    )
    
    # Informações do produto
    codigo_produto = models.CharField(
        "Código do Produto (SKU)",
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Código de barras ou SKU. Deve ser único."
    )
    marca = models.CharField(max_length=100, blank=True)
    peso = models.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        blank=True, 
        null=True,
        help_text="Peso em kg"
    )
    dimensoes = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Dimensões do produto (ex: 10x20x30 cm)"
    )
    
    # Datas importantes
    data_fabricacao = models.DateField(
        "Data de Fabricação",
        blank=True,
        null=True
    )
    data_validade = models.DateField(
        "Data de Validade",
        blank=True,
        null=True,
        help_text="Importante para produtos perecíveis."
    )
    
    # Controle de estoque
    quantidade_estoque = models.PositiveIntegerField(
        default=0,
        help_text="Quantidade total que o vendedor tem disponível."
    )
    estoque_minimo = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade mínima para alerta de estoque baixo"
    )
    
    # Status e controles
    ativo = models.BooleanField(
        default=True,
        help_text="O vendedor pode desmarcar para 'pausar' o anúncio do produto."
    )
    destaque = models.BooleanField(
        default=False,
        help_text="Produto em destaque na página inicial"
    )
    
    # Métricas
    visualizacoes = models.PositiveIntegerField(
        default=0,
        help_text="Número de visualizações do produto"
    )
    vendas_totais = models.PositiveIntegerField(
        default=0,
        help_text="Total de unidades vendidas"
    )
    
    # Avaliações
    avaliacao_media = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_avaliacoes = models.PositiveIntegerField(default=0)

    objects = ProdutoManager()

    data_fabricacao = models.DateField("Data de Fabricação", blank=True, null=True)
    data_validade = models.DateField("Data de Validade", blank=True, null=True)
    
    quantidade_estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True) 

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['ativo', 'quantidade_estoque']),
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['vendedor', 'ativo']),
            models.Index(fields=['-data_criacao']),
            models.Index(fields=['destaque', 'ativo']),
        ]

    def __str__(self):
        return f'{self.nome} | {self.vendedor.nome_negocio or self.vendedor.usuario.username}'

    def get_absolute_url(self):
        return reverse('core:produto_detalhe', kwargs={'produto_id': self.pk})
    
    @property
    def imagem(self):
        """Propriedade para compatibilidade com código existente"""
        return self.imagem_principal
    
    @property
    def disponivel_para_venda(self):
        """Verifica se o produto está disponível para venda"""
        return self.ativo and self.quantidade_estoque > 0
    
    @property
    def estoque_baixo(self):
        """Verifica se o estoque está baixo"""
        return self.quantidade_estoque <= self.estoque_minimo
    
    @property
    def vencimento_proximo(self):
        """Verifica se o produto está próximo do vencimento (30 dias)"""
        if not self.data_validade:
            return False
        return (self.data_validade - timezone.now().date()).days <= 30
    
    def incrementar_visualizacoes(self):
        """Incrementa o contador de visualizações"""
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])
    
    def save(self, *args, **kwargs):
        # Gerar código do produto se não fornecido
        if not self.codigo_produto:
            self.codigo_produto = f'PROD-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nome} | Vendedor: {self.vendedor.usuario.username}'

