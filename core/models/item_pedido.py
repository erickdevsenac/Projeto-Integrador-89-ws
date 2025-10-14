from django.core.validators import MinValueValidator
from django.db import models

from .time_stamp import TimeStampedModel


class ItemPedido(TimeStampedModel):
    """
    Representa um item de produto específico dentro de um PedidoVendedor (sub-pedido).
    """

    sub_pedido = models.ForeignKey(
        "core.PedidoVendedor", on_delete=models.CASCADE, related_name="itens"
    )
    produto = models.ForeignKey(
        "core.Produto",
        on_delete=models.PROTECT,
        related_name="itens_pedidos",
        null=True,
        blank=True,
    )
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    # Armazena o preço no momento da compra para preservar o histórico
    preco_unitario = models.DecimalField(
        "Preço Unitário na Compra",
        max_digits=10,
        decimal_places=2,
    )

    pacote_surpresa = models.ForeignKey(
        "core.PacoteSurpresa",
        on_delete=models.PROTECT,
        related_name="itens_pedidos",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"
        # Garante que o mesmo produto não seja adicionado duas vezes no mesmo sub-pedido
        # unique_together = ("sub_pedido", "produto")

    def __str__(self):
        if self.produto:
            return f"{self.quantidade}x {self.produto.nome}"
        elif self.pacote_surpresa:
            return f"{self.quantidade}x {self.pacote_surpresa.nome}"
        return "Item Inválido"

    @property
    def subtotal(self):
        """Calcula o subtotal do item."""
        return self.quantidade * self.preco_unitario
