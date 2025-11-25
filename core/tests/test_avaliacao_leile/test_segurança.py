import pytest
from rest_framework.test import APIClient
from core.models import Produto, CategoriaProduto, Perfil

@pytest.mark.django_db
def test_nao_autorizado_nao_pode_deletar_produto():
    # ARRANGE
    categoria = CategoriaProduto.objects.create(nome="Aproveite+", slug="aproveite")
    vendedor = Perfil.objects.create(usuario_id=1, tipo="VENDEDOR", nome_negocio="Mercado Teste")
    produto = Produto.objects.create(nome="Banana", preco=10, quantidade_estoque=5, categoria=categoria, vendedor=vendedor, ativo=True)
    client = APIClient()  

    # ACT
    resposta = client.delete(f"/api/produto/{produto.id}/")

    # ASSERT
    assert resposta.status_code in [401, 403], "Usuário não autenticado não deveria conseguir deletar produto."
