from django.db import models

from .perfil import Perfil
from .produto import PacoteSurpresa, Produto
from .time_stamp import TimeStampedModel


class Carrinho(TimeStampedModel):
    """
    Representa o carrinho de compras de um usuário.
    """

    usuario = models.OneToOneField(
        Perfil, on_delete=models.CASCADE, related_name="carrinho"
    )

    def __str__(self):
        return f"Carrinho de {self.usuario}"


class ItemCarrinho(TimeStampedModel):
    """
    Representa um item (Produto ou Pacote) dentro de um carrinho.
    """

    carrinho = models.ForeignKey(
        Carrinho, on_delete=models.CASCADE, related_name="itens"
    )
    quantidade = models.PositiveIntegerField(default=1)

    # Relação para o item, pode ser um Produto ou um Pacote Surpresa
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, null=True, blank=True
    )
    pacote = models.ForeignKey(
        PacoteSurpresa, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        if self.produto:
            return f"{self.quantidade}x {self.produto.nome}"
        if self.pacote:
            return f"{self.quantidade}x {self.pacote.nome}"
        return "Item inválido"

    @property
    def subtotal(self):
        if self.produto:
            return self.produto.preco * self.quantidade
        if self.pacote:
            return self.pacote.preco * self.quantidade
        return 0
