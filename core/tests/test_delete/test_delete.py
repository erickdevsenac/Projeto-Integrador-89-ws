import pytest
from core.models import Produto
 
@pytest.mark.django_db
def test_deve_reduzir_a_contagem_apos_deletar(django_user_model):
    #ARRANGE
    vendedor = django_user_model.objects.create_user(username='vendedor_teste', password='123')
   
    Produto.objects.create(nome="Produto A", preco=10.00, vendedor=vendedor)
    produto_a_deletar = Produto.objects.create(nome="Produto B", preco=20.00, vendedor=vendedor)
   
    assert Produto.objects.count() == 2
   
    #ACT
    produto_a_deletar.delete()
   
    #ASSERT
    assert Produto.objects.count() == 1