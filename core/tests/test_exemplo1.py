import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from core.models.perfil import Perfil
from core.models.produto import Produto

@pytest.fixture
def api_client():
    """Fixture para o cliente de API do Django REST Framework."""
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
def test_listagem_produtos_apenas_disponiveis(api_client, vendedor_fixture):
    """
    Testa se a API lista apenas produtos ativos e com estoque[cite: 116].
    """

    # 1. Arrange (Preparar): Criar cenários de teste 

    # Produto 1: Disponível (Deve aparecer na lista)
    Produto.objects.create(
        vendedor=vendedor_fixture,
        nome="P1 Disponível",
        preco=10.00,
        quantidade_estoque=5,
        ativo=True,
    )

    # Produto 2: Indisponível (Estoque zero NÃO deve aparecer)
    Produto.objects.create(
        vendedor=vendedor_fixture,
        nome="P2 Sem Estoque",
        preco=20.00,
        quantidade_estoque=0,
        ativo=True,
    )

    # Produto 3: Indisponível (Inativo NÃO deve aparecer)
    Produto.objects.create(
        vendedor=vendedor_fixture,
        nome="P3 Inativo",
        preco=30.00,
        quantidade_estoque=10,
        ativo=False,
    )

    # 2. Act (Executar): Fazer a requisição GET para o endpoint [cite: 134]
    response = api_client.get("/api/produto/")

    # 3. Assert (Verificar): Validar o resultado [cite: 135]
    assert response.status_code == 200
    data = response.json()

    # Verifica se apenas 1 produto (o disponível) foi retornado
    assert len(data) == 1
    assert data[0]["nome"] == "P1 Disponível"