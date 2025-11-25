from decimal import Decimal
import pytest
 
@pytest.mark.parametrize("quantidade, preco, total_esperado", [
    (2, Decimal("5.00"), Decimal("10.00"))
])
 
# ARRANGE
def test_calculo_total_simples(quantidade, preco, total_esperado):
   
    # ACT
    total = quantidade * preco
   
    # ASSERT
    assert total == total_esperado
 
 