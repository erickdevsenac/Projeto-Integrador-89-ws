from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

from .time_stamp import TimeStampedModel
from core.models.produto import CategoriaProduto

class Cupom(TimeStampedModel):
    """Modelo para cupons de desconto"""
    
    class TipoDesconto(models.TextChoices):
        PERCENTUAL = "PERCENTUAL", "% Percentual"
        VALOR_FIXO = "VALOR_FIXO", "R$ Valor Fixo"
 
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código que o cliente irá usar (ex: PROMO10)",
    )
    
    nome = models.CharField(
        max_length=100,
        help_text="Nome descritivo do cupom"
    )
    
    descricao = models.TextField(
        blank=True,
        help_text="Descrição detalhada da promoção"
    )
    
    tipo_desconto = models.CharField(
        max_length=20, 
        choices=TipoDesconto.choices, 
        default=TipoDesconto.PERCENTUAL
    )
    
    valor_desconto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Restrições de uso
    data_inicio = models.DateTimeField(
        default=timezone.now,
        help_text="Data de início da validade do cupom"
    )
     
    data_validade = models.DateTimeField(
        null=True,
        blank=True,
        help_text="O cupom não será válido após esta data. Deixe em branco para não expirar.",
    )

    limite_uso = models.PositiveIntegerField(
        default=1, 
        help_text="Quantas vezes este cupom pode ser usado no total."
    )
 
    valor_minimo_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Valor mínimo da compra para aplicar o cupom"
    )
    
    valor_maximo_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor máximo de desconto (apenas para cupons percentuais)"
    )
    
    # Controles
    ativo = models.BooleanField(default=True)
    usos_realizados = models.PositiveIntegerField(
        default=0, 
        editable=False,
        help_text="Contador de usos realizados"
    )
    
    # Restrições por categoria ou vendedor
    categorias_permitidas = models.ManyToManyField(
        CategoriaProduto,
        blank=True,
        help_text="Categorias onde o cupom pode ser aplicado (vazio = todas)"
    )
    
    vendedores_permitidos = models.ManyToManyField(
        'core.Perfil',
        blank=True,
        limit_choices_to={'tipo': 'VENDEDOR'},
        help_text="Vendedores onde o cupom pode ser aplicado (vazio = todos)"
    )

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['ativo', 'data_validade']),
        ]

    def __str__(self):
        if self.tipo_desconto == self.TipoDesconto.PERCENTUAL:
            return f"{self.codigo} ({int(self.valor_desconto)}%)"
        return f"{self.codigo} (R$ {self.valor_desconto})"
    
    @property
    def esta_valido(self):
        """Verifica se o cupom está válido"""
        agora = timezone.now()
        return (
            self.ativo and
            self.data_inicio <= agora and
            (not self.data_validade or self.data_validade >= agora) and
            self.usos_realizados < self.limite_uso
        )
    
    @property
    def usos_restantes(self):
        """Retorna quantos usos restam"""
        return max(0, self.limite_uso - self.usos_realizados)
    
    def calcular_desconto(self, valor_pedido):
        """Calcula o valor do desconto para um pedido"""
        if not self.esta_valido or valor_pedido < self.valor_minimo_compra:
            return Decimal('0.00')
        
        if self.tipo_desconto == self.TipoDesconto.PERCENTUAL:
            desconto = valor_pedido * (self.valor_desconto / 100)
            if self.valor_maximo_desconto:
                desconto = min(desconto, self.valor_maximo_desconto)
        else:
            desconto = self.valor_desconto
        
        # Desconto não pode ser maior que o valor do pedido
        return min(desconto, valor_pedido)
    
    def usar_cupom(self):
        """Incrementa o contador de uso do cupom"""
        self.usos_realizados += 1
        self.save(update_fields=['usos_realizados']) 
 