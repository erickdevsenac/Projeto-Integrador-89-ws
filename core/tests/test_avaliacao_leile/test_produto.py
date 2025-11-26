import pytest
from core.models import Produto, CategoriaProduto, Perfil
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_produtos_com_estoque_zero_que_nao_aparecem_na_interface():
    # ARRANGE
    categoria = CategoriaProduto.objects.create(nome="Frutas", slug="frutas")
    vendedor = Perfil.objects.create(usuario= user ,tipo="VENDEDOR", nome_negocio="Mercado Teste")
    user = User.objects.create_user(username="testevendedor",email="vendedor@teste.com",password="senhaforte123")

    # Criação do produto com estoque zero
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
    assert produtos_estoque_zero.count() == 1  # Espera-se que o produto com estoque 0 apareça
