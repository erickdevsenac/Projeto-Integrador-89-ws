import pytest
from rest_framework.test import APIClient
from core.models import Produto, CategoriaProduto, Perfil
from django.contrib.auth.models import User  # Importing the User model

@pytest.mark.django_db
def test_nao_autorizado_nao_pode_deletar_produto():
    # ARRANGE
    categoria = CategoriaProduto.objects.create(nome="Aproveite+", slug="aproveite")

    user = User.objects.create_user(username="testevendedor", email="vendedor@teste.com", password="senhaforte123")
    vendedor = Perfil.objects.create(usuario=user, tipo="VENDEDOR", nome_negocio="Mercado Teste")
 
    produto = Produto.objects.create(nome="Banana", preco=10, quantidade_estoque=5, categoria=categoria, vendedor=vendedor, ativo=True)
    client = APIClient()  

    # ACT - Tentativa de deletar o produto sem autenticação
    resposta = client.delete(f"/api/produto/{produto.id}/")  

    # ASSERT - Verificar se o código de status é 401 (não autorizado) ou 403 (proibido)
    assert resposta.status_code in [401, 403], "Usuário não autenticado não deveria conseguir deletar produto."
