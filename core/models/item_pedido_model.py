from django.db import models

class ItemPedido(models.Model):
    """
    Representa um item específico dentro do sub-pedido de um vendedor.
    """
    # A qual sub-pedido este item pertence?
    # Este é o vínculo principal na lógica do marketplace.
    sub_pedido = models.ForeignKey(
        'core.PedidoVendedor', # Usando string para evitar importação circular
        on_delete=models.CASCADE,
        related_name='itens'
    )

    # Qual produto está sendo comprado?
    # Protegemos o produto para que ele não possa ser deletado se estiver em um pedido.
    produto = models.ForeignKey(
        'core.Produto', # Usando string para evitar importação circular
        on_delete=models.PROTECT,
        related_name='itens_pedidos'
    )
    
    quantidade = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade de unidades do produto neste item."
    )
    
    # Campo para o preço no momento da compra.
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço do produto no momento da compra. Preenchido automaticamente se deixado em branco.",
        null=True, # Permite que o campo fique temporariamente nulo antes de salvar
        blank=True
    )

    class Meta:
        # Garante que um produto não possa ser adicionado duas vezes ao mesmo sub-pedido.
        unique_together = ('sub_pedido', 'produto')
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"

    def save(self, *args, **kwargs):
        # Se o preço unitário não foi definido, busca o preço do produto relacionado
        if self.preco_unitario is None and self.produto:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs) # Chama o método save original

    def subtotal(self):
        if self.quantidade and self.preco_unitario is not None:
            return self.quantidade * self.preco_unitario
        return 0
    
    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} (Sub-Pedido: #{self.sub_pedido.id})'