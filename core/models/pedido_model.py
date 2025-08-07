from django.db import models
from django.utils import timezone

# ---
# Modelo Principal: O pedido do ponto de vista do Cliente
# ---
class Pedido(models.Model):
    class FormaPagamento(models.TextChoices):
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
        PIX = 'PIX', 'Pix'
        CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    
    class StatusPagamento(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Pagamento'
        PAGO = 'PAGO', 'Pago'
        FALHA = 'FALHA', 'Falha no Pagamento'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    # Quem fez o pedido?
    cliente = models.ForeignKey(
        'core.Perfil',
        on_delete=models.PROTECT, # Protege o pedido se o cliente for deletado
        related_name='pedidos',
        limit_choices_to={'tipo': 'CLIENTE'}
    )
    
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Alterado para DateTimeField para registrar a hora exata do pedido
    data_pedido = models.DateTimeField(default=timezone.now)
    
    endereco_entrega = models.CharField(max_length=255)
    
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

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.usuario.username}"

# ---
# Modelo do Sub-Pedido: A parte que cada Vendedor gerencia
# ---
class PedidoVendedor(models.Model):
    class StatusPedidoVendedor(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Aprovação'
        EM_PREPARO = 'EM_PREPARO', 'Em Preparo'
        A_CAMINHO = 'A_CAMINHO', 'A Caminho'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADO = 'CANCELADO', 'Cancelado'
        
    pedido_principal = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='sub_pedidos')
    
    # Qual vendedor é responsável por este sub-pedido?
    vendedor = models.ForeignKey(
        'core.Perfil',
        on_delete=models.PROTECT,
        related_name='pedidos_recebidos',
        limit_choices_to={'tipo': 'VENDEDOR'}
    )
    
    status = models.CharField(max_length=20, choices=StatusPedidoVendedor.choices, default=StatusPedidoVendedor.AGUARDANDO)
    valor_subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor total dos itens deste vendedor.")
    
    def __str__(self):
        return f"Sub-Pedido para {self.vendedor.nome_negocio} (Pedido #{self.pedido_principal.id})"