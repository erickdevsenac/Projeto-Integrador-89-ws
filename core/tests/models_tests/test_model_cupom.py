from core.models.cupom import Cupom
from django.utils import timezone
from datetime import timedelta
import pytest

@pytest.mark.django_db
def test_cupom_vencido_deve_ser_invalido():
    data_ontem = timezone.now() - timedelta(days=1)
    data_inicio = timezone.now() - timedelta(days=3)
    cupom_vencido = Cupom.objects.create(
        codigo = "VENCEUONTEM",
        tipo_desconto = Cupom.TipoDesconto.PERCENTUAL,
        valor_desconto = 10,
        limite_uso = 5,
        data_validade = data_ontem,
        data_inicio = data_inicio,
        valor_minimo_compra = 2.50,
        ativo = True
    )
    
    valido = cupom_vencido.esta_valido
    assert valido is False