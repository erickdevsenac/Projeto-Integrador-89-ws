from django.db import models
from .time_stamp_model import TimeStampedModel
from .pedido_model import Pedido

class PedidoVendedor(TimeStampedModel):
    """Modelo melhorado para sub-pedidos dos vendedores"""
    
    class StatusPedidoVendedor(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Aprovação'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        EM_PREPARO = 'EM_PREPARO', 'Em Preparo'
        PRONTO = 'PRONTO', 'Pronto para Retirada'
        A_CAMINHO = 'A_CAMINHO', 'A Caminho'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADO = 'CANCELADO', 'Cancelado'
        
    pedido_principal = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='sub_pedidos'
    )
    
    vendedor = models.ForeignKey(
        'core.Perfil',
        on_delete=models.PROTECT,
        related_name='pedidos_recebidos',
        limit_choices_to={'tipo': 'VENDEDOR'}
    )
    
    status = models.CharField(
        max_length=20, 
        choices=StatusPedidoVendedor.choices, 
        default=StatusPedidoVendedor.AGUARDANDO
    )
    
    valor_subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Valor total dos itens deste vendedor."
    )
    
    # Informações de entrega
    codigo_rastreamento = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Código de rastreamento da transportadora"
    )
    previsao_entrega = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Previsão de entrega"
    )
    data_entrega = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Data efetiva da entrega"
    )
    
    # Observações do vendedor
    observacoes_vendedor = models.TextField(blank=True)

    class Meta:
        verbose_name = "Sub-Pedido do Vendedor"
        verbose_name_plural = "Sub-Pedidos dos Vendedores"
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['vendedor', '-data_criacao']),
            models.Index(fields=['status']),
            models.Index(fields=['pedido_principal']),
        ]

    def __str__(self):
        return f"Sub-Pedido para {self.vendedor.nome_negocio} (Pedido #{self.pedido_principal.numero_pedido})"
    
    @property
    def pode_ser_cancelado(self):
        """Verifica se o sub-pedido pode ser cancelado"""
        return self.status in [
            self.StatusPedidoVendedor.AGUARDANDO,
            self.StatusPedidoVendedor.CONFIRMADO
        ]