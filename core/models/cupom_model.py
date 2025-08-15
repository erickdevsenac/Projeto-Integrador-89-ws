# Em core/models.py
from django.db import models
from django.utils import timezone


class Cupom(models.Model):
    class TipoDesconto(models.TextChoices):
        PERCENTUAL = "PERCENTUAL", "% Percentual"
        VALOR_FIXO = "VALOR_FIXO", "R$ Valor Fixo"

    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código que o cliente irá usar (ex: PROMO10)",
    )
    tipo_desconto = models.CharField(
        max_length=20, choices=TipoDesconto.choices, default=TipoDesconto.PERCENTUAL
    )
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2)

    data_validade = models.DateField(
        null=True,
        blank=True,
        help_text="O cupom não será válido após esta data. Deixe em branco para não expirar.",
    )

    ativo = models.BooleanField(default=True)
    usos_realizados = models.PositiveIntegerField(
        default=0, editable=False
    )  # Para contar os usos

    limite_uso = models.PositiveIntegerField(  # CORREÇÃO: Nome padronizado
        default=1, help_text="Quantas vezes este cupom pode ser usado no total."
    )

    valor_minimo_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,  # CORREÇÃO: Adicionado valor padrão
    )

    def __str__(self):
        if self.tipo_desconto == self.TipoDesconto.PERCENTUAL:
            return f"{self.codigo} ({int(self.valor_desconto)}%)"
        return f"{self.codigo} (R$ {self.valor_desconto})"
