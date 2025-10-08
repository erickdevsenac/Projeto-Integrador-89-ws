import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse
from .time_stamp import TimeStampedModel

def gerar_numero_pedido():
    """Gera um número de pedido único e legível."""
    return f"PED-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

class Pedido(TimeStampedModel):
    """Modelo para o pedido principal do cliente."""
    
    class FormaPagamento(models.TextChoices):
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
        PIX = 'PIX', 'Pix'
        BOLETO = 'BOLETO', 'Boleto Bancário'
    
    class StatusPagamento(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Pagamento'
        PAGO = 'PAGO', 'Pago'
        FALHA = 'FALHA', 'Falha no Pagamento'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    numero_pedido = models.CharField(
        max_length=30, 
        unique=True, 
        default=gerar_numero_pedido,
        editable=False
    )
    
    cliente = models.ForeignKey(
        'core.Perfil',
        on_delete=models.PROTECT,
        related_name='pedidos',
        limit_choices_to={'tipo': 'CLIENTE'}
    )
    
    valor_produtos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    endereco_entrega = models.TextField()
    
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
    
    cupom_aplicado = models.ForeignKey(
        'core.Cupom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_utilizados'
    )
    
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.cliente}"
    
    def save(self, *args, **kwargs):
        # Garante que o valor total seja sempre calculado antes de salvar
        self.valor_total = (self.valor_produtos + self.valor_frete) - self.valor_desconto
        super().save(*args, **kwargs)