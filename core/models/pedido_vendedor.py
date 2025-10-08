from django.db import models
from .time_stamp import TimeStampedModel

class PedidoVendedor(TimeStampedModel):
    """Modelo para o sub-pedido, gerenciado por cada vendedor."""
    
    class StatusPedidoVendedor(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Aprovação'
        EM_PREPARO = 'EM_PREPARO', 'Em Preparo'
        A_CAMINHO = 'A_CAMINHO', 'A Caminho'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADO = 'CANCELADO', 'Cancelado'
        
    pedido_principal = models.ForeignKey(
        'core.Pedido', 
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
        help_text="Valor total dos itens deste vendedor neste pedido."
    )
    
    codigo_rastreamento = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Sub-Pedido (Vendedor)"
        verbose_name_plural = "Sub-Pedidos (Vendedores)"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Sub-Pedido para {self.vendedor.nome_negocio} ({self.pedido_principal.numero_pedido})"