import pytest
from django.utils import timezone
from datetime import timedelta
from core.models import Cupom

@pytest.mark.django_db
def test_cupom_vencido_deve_ser_invalido():
    # Arrange: cria um cupom cuja validade já expirou ontem
    ontem = timezone.now() - timedelta(days=1)

    cupom = Cupom.objects.create(
        codigo="EXPIRED10",
        nome="Cupom Vencido",
        descricao="Não deve ser aceito",
        tipo_desconto=Cupom.TipoDesconto.PERCENTUAL,
        valor_desconto=10,
        data_inicio=timezone.now() - timedelta(days=10),
        data_validade=ontem,
        limite_uso=5,
        valor_minimo_compra=0,
        ativo= True
    )

    # Act
    resultado = cupom.esta_valido

    # Assert
    assert resultado is False
