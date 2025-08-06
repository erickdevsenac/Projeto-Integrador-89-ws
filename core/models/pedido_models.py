from django.db import models
from django.utils import timezone

# ---
# Modelo Principal: O pedido do ponto de vista do Cliente
# ---
class Pedido(models.Model):
    # Classes TextChoices para modernizar e organizar os 'choices'
    class FormaPagamento(models.TextChoices):
        CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
        PIX = 'PIX', 'Pix'
        CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    
    class StatusPagamento(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando Pagamento'
        PAGO = 'PAGO', 'Pago'
        FALHA = 'FALHA', 'Falha no Pagamento'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    # RELACIONAMENTO CRÍTICO: Quem fez o pedido?
    cliente = models.ForeignKey(
        'loja.Perfil', # Supondo que seu Perfil está no app 'loja'
        on_delete=models.PROTECT, # Protege o pedido se o cliente for deletado
        related_name='pedidos',
        limit_choices_to={'tipo': 'CLIENTE'}
    )
    
    # O 'id' padrão do Django é melhor que um AutoField manual
    # id = models.AutoField(primary_key=True) -> Removido por ser redundante

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
        # __str__ mais limpo para o painel de admin
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
        
    # Relação com o pedido principal (estava correto)
    pedido_principal = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='sub_pedidos')
    
    # RELACIONAMENTO CRÍTICO: Qual vendedor é responsável por este sub-pedido?
    vendedor = models.ForeignKey(
        'loja.Perfil', # Descomentado e ajustado
        on_delete=models.PROTECT,
        related_name='pedidos_recebidos',
        limit_choices_to={'tipo': 'VENDEDOR'}
    )
    
    status = models.CharField(max_length=20, choices=StatusPedidoVendedor.choices, default=StatusPedidoVendedor.AGUARDANDO)
    valor_subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor total dos itens deste vendedor.")
    
    def __str__(self):
        # Acessa o nome do negócio do vendedor, que está no Perfil
        return f"Sub-Pedido para {self.vendedor.nome_negocio} (Pedido #{self.pedido_principal.id})"