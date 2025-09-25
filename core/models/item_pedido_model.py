from django.db import models
from .pedido_vendedor import PedidoVendedor
from .produto_model import Produto

class ItemPedido(models.Model):
    """Modelo melhorado para itens do pedido"""
    
    sub_pedido = models.ForeignKey(
        PedidoVendedor,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedidos'
    )
    
    quantidade = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade de unidades do produto neste item."
    )
    
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Preço do produto no momento da compra."
    )
    
    # Informações adicionais do produto no momento da compra
    nome_produto = models.CharField(
        max_length=200,
        help_text="Nome do produto no momento da compra"
    )
    codigo_produto = models.CharField(
        max_length=50,
        blank=True,
        help_text="Código do produto no momento da compra"
    )

    class Meta:
        unique_together = ('sub_pedido', 'produto')
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"
        indexes = [
            models.Index(fields=['sub_pedido']),
            models.Index(fields=['produto']),
        ]

    def save(self, *args, **kwargs):
        # Preencher informações do produto automaticamente
        if not self.nome_produto and self.produto:
            self.nome_produto = self.produto.nome
        if not self.codigo_produto and self.produto:
            self.codigo_produto = self.produto.codigo_produto or ''
        if not self.preco_unitario and self.produto:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

    def subtotal(self):
        """Calcula o subtotal do item"""
        if self.quantidade and self.preco_unitario is not None:
            return self.quantidade * self.preco_unitario
        return 0
    
    def __str__(self):
        return f'{self.quantidade}x {self.nome_produto} (Sub-Pedido: #{self.sub_pedido.id})'