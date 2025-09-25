from django.db import models
from django.utils import timezone
from django.urls import reverse
import uuid

from .time_stamp_model import TimeStampedModel

class Pedido(TimeStampedModel):
    """Modelo para pedidos"""
    
    class FormaPagamento(models.TextChoices):
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
        PIX = 'PIX', 'Pix'
        CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
        BOLETO = 'BOLETO', 'Boleto Bancário'
    
    class StatusPagamento(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Pagamento'
        PAGO = 'PAGO', 'Pago'
        FALHA = 'FALHA', 'Falha no Pagamento'
        CANCELADO = 'CANCELADO', 'Cancelado'
        ESTORNADO = 'ESTORNADO', 'Estornado'
    
    # Identificação única do pedido
    numero_pedido = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        help_text="Número único do pedido"
    )
    
    # Relacionamentos
    cliente = models.ForeignKey(
        'core.Perfil',
        on_delete=models.PROTECT,
        related_name='pedidos',
        limit_choices_to={'tipo': 'CLIENTE'}
    )
    
    # Valores
    valor_produtos = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Valor total dos produtos"
    )
    valor_frete = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Valor do frete"
    )
    valor_desconto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Valor do desconto aplicado"
    )
    valor_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Valor final do pedido"
    )
    
    # Informações de entrega
    endereco_entrega = models.TextField()
    cep_entrega = models.CharField(max_length=10, blank=True)
    cidade_entrega = models.CharField(max_length=100, blank=True)
    estado_entrega = models.CharField(max_length=2, blank=True)
    
    # Informações de pagamento
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FormaPagamento.choices,
        default=FormaPagamento.PIX
    )
    status_pagamento = models.CharField(
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.AGUARDANDO
    )
    
    # Cupom aplicado
    cupom_aplicado = models.ForeignKey(
        'core.Cupom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_utilizados'
    )
    
    # Observações
    observacoes = models.TextField(blank=True)
    
    # Timestamps específicos
    data_pagamento = models.DateTimeField(null=True, blank=True)
    data_cancelamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['cliente', '-data_criacao']),
            models.Index(fields=['status_pagamento']),
            models.Index(fields=['numero_pedido']),
        ]

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente.usuario.username}"
    
    def get_absolute_url(self):
        return reverse('core:pedido_detalhe', kwargs={'pedido_id': self.pk})
    
    def save(self, *args, **kwargs):
        # Gerar número do pedido se não fornecido
        if not self.numero_pedido:
            self.numero_pedido = f'{timezone.now().year}{self.pk or ""}{uuid.uuid4().hex[:6].upper()}'
        
        # Calcular valor total
        self.valor_total = self.valor_produtos + self.valor_frete - self.valor_desconto
        
        super().save(*args, **kwargs)
    
    @property
    def pode_ser_cancelado(self):
        """Verifica se o pedido pode ser cancelado"""
        return self.status_pagamento in [
            self.StatusPagamento.AGUARDANDO,
            self.StatusPagamento.FALHA
        ]