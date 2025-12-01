import pytest
from rest_framework.test import APIClient
from core.models.produto import Produto
from core.models.perfil import Perfil
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def vendedor_fixture():
    """Fixture que cria um usuário VENDEDOR e seu Perfil."""
    # Cria o usuário django
    user = User.objects.create_user(
        username="testevendedor",
        email="vendedor@teste.com",
        password="senhaforte123"
    )
   
    # Usamos a string direta 'V' em vez de Perfil.TipoPerfil.VENDEDOR
    # Se o seu banco espera a palavra completa, troque 'V' por 'VENDEDOR'
    perfil = Perfil.objects.create(
        usuario=user,
        tipo='V',
        nome_negocio="Mercado Teste"
    )
    return perfil

@pytest.mark.django_db
class TestProdutoModel:
    def test_listagem_produtos_apenas_disponveis(self,api_client, vendedor_fixture):
        #ARRANGE
        Produto.objects.create(
            vendedor = vendedor_fixture,
            nome = "Produto1 disponível",
            preco = 2.00,
            quantidade_estoque=2,
            ativo=True
        )
        
        Produto.objects.create(
            vendedor = vendedor_fixture,
            nome = "Produto2 Sem Estoque",
            preco = 23.00,
            quantidade_estoque=0,
            ativo=True
        )
        
        Produto.objects.create(
            vendedor = vendedor_fixture,
            nome = "Produto3 Inativo",
            preco = 17.00,
            quantidade_estoque=3,
            ativo=False
        )
        
        # ACT (Execução)
        response = api_client.get("/api/produto/")
        
        # Assert
        assert response.status_code is 200
        
        
        dados = response.json()
        assert dados['count'] == 1
        
        assert len(dados['results']) == 1
        assert dados['results'][0]['nome'] == "Produto1 disponível"