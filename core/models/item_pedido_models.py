from django.db import models

class ItemPedido(models.Model):
    """
    Representa um item específico dentro do sub-pedido de um vendedor.
    """
    # RELACIONAMENTO 1: A qual sub-pedido este item pertence?
    # Este é o vínculo principal na lógica do marketplace.
    sub_pedido = models.ForeignKey(
        'loja.PedidoVendedor', # Usando string para evitar importação circular
        on_delete=models.CASCADE,
        related_name='itens'
    )

    # RELACIONAMENTO 2: Qual produto está sendo comprado?
    # Protegemos o produto para que ele não possa ser deletado se estiver em um pedido.
    produto = models.ForeignKey(
        'loja.Produto', # Usando string para evitar importação circular
        on_delete=models.PROTECT,
        related_name='itens_pedidos'
    )
    
    # Campo para a quantidade do item. Está correto.
    quantidade = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade de unidades do produto neste item."
    )
    
    # Campo para o preço no momento da compra. Está correto e é uma ótima prática.
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço do produto no momento em que o pedido foi feito."
    )

    # O campo 'categoria_produto' foi removido por ser redundante.

    class Meta:
        # Garante que um produto não possa ser adicionado duas vezes ao mesmo sub-pedido.
        unique_together = ('sub_pedido', 'produto')
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"

    def subtotal(self):
        """Calcula o valor total para este item (quantidade * preço)."""
        return self.quantidade * self.preco_unitario

    def __str__(self):
        """
        Corrige o método __str__ para ter apenas uma definição e ser mais informativo.
        """
        return f'{self.quantidade}x {self.produto.nome} (Sub-Pedido: #{self.sub_pedido.id})'