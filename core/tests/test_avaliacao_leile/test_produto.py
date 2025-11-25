import pytest
from core.models import Produto, CategoriaProduto, Perfil

@pytest.mark.django_db
def test_produtos_com_estoque_zero():
    # ARRANGE
    categoria = CategoriaProduto.objects.create(nome="Frutas", slug="frutas")
    vendedor = Perfil.objects.create(usuario_id=1, tipo="VENDEDOR", nome_negocio="Mercado Teste")

    Produto.objects.create(
        nome="Banana",
        preco=10,
        quantidade_estoque=0,
        categoria=categoria,
        vendedor=vendedor,
        ativo=True
    )

    # ACT
    produtos_estoque_zero = Produto.objects.filter(quantidade_estoque=0)

    # ASSERT
    assert produtos_estoque_zero.count() == 1
