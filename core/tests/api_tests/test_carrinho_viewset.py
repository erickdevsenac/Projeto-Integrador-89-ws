"""
Testes de integração para CarrinhoViewSet (core/viewsets/carrinho_viewset.py)

Endpoints cobertos:
  GET    /api/carrinho/           — list (get_or_create carrinho do usuário)
  POST   /api/carrinho/adicionar_item/  — action: adicionar_item
  POST   /api/carrinho/{pk}/remover-item/ — action: remover_item (pk=ItemCarrinho.id)

Permission: IsAuthenticated em todas as ações
Fixtures: conftest.py + fixtures locais para Produto/PacoteSurpresa
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Produto, PacoteSurpresa, Perfil
from core.models.carrinho import Carrinho, ItemCarrinho
from core.tests.conftest import vendedor_fake 


@pytest.fixture
def api_client():
    """APIClient para testes autenticados."""
    return APIClient()


@pytest.fixture
def cliente_auth(api_client, cliente_fake):
    """Cliente autenticado — retorna APIClient com token do cliente_fake."""
    api_client.force_authenticate(user=cliente_fake.usuario)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def vendedor_auth(api_client, vendedor_fake):
    """Vendedor autenticado — para testar isolamento de dados."""
    api_client.force_authenticate(user=vendedor_fake.usuario)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def produto_cliente(cliente_fake):
    """Produto com estoque para adicionar ao carrinho do cliente."""
    return Produto.objects.create(
        nome="Banana Orgânica",
        preco=10.00,
        quantidade_estoque=5,
        vendedor=cliente_fake,  # vendedor pode vender para si mesmo em test
        ativo=True,
    )


@pytest.fixture
def pacote_surpresa_cliente(cliente_fake):
    """PacoteSurpresa com estoque para testar adicionar pacote."""
    return PacoteSurpresa.objects.create(
        nome="Pacote Surpresa Frutas",
        preco=25.00,
        quantidade_estoque=3,
        vendedor=cliente_fake,
    )


@pytest.fixture
def item_carrinho_cliente(produto_cliente, cliente_fake):
    """ItemCarrinho pré-existente para testar remover_item."""
    carrinho = Carrinho.objects.get_or_create(usuario=cliente_fake)[0]
    return ItemCarrinho.objects.create(
        carrinho=carrinho,
        produto=produto_cliente,
        quantidade=2,
    )


@pytest.mark.django_db
class TestCarrinhoViewSet:
    def test_list_sem_itens_retorna_carrinho_vazio(self, cliente_auth, produto_cliente):
        """
        GET /api/carrinho/ → 200 com carrinho vazio mas estruturado.
        Confirma get_or_create do CarrinhoViewSet.list().
        """
        resposta = cliente_auth.get("/api/carrinho/")

        assert resposta.status_code == status.HTTP_200_OK
        assert "id" in resposta.data
        assert "usuario" in resposta.data
        assert resposta.data["itens"] == []  # vazio inicialmente

    def test_list_com_itens_retorna_carrinho_populado(self, cliente_auth, item_carrinho_cliente):
        """
        GET /api/carrinho/ → 200 com itens serializados.
        """
        resposta = cliente_auth.get("/api/carrinho/")

        assert resposta.status_code == status.HTTP_200_OK
        assert len(resposta.data["itens"]) == 1
        assert resposta.data["itens"][0]["quantidade"] == 2

   

    def test_list_sem_autenticacao_retorna_401(self, api_client):
        """
        Permission IsAuthenticated: não autenticado → 401.
        """
        resposta = api_client.get("/api/carrinho/")
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED

    def test_adicionar_item_produto_com_estoque_suficiente(self, cliente_auth, produto_cliente):
        """
        POST /api/carrinho/adicionar_item/ com produto_id → 200, atualiza carrinho.
        """
        payload = {"produto_id": produto_cliente.id, "quantidade": 1}

        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", payload, format="json")

        assert resposta.status_code == status.HTTP_200_OK
        assert len(resposta.data["itens"]) == 1
        assert resposta.data["itens"][0]["quantidade"] == 1
        assert ItemCarrinho.objects.filter(produto=produto_cliente).exists()

    def test_adicionar_item_pacote_surpresa(self, cliente_auth, pacote_surpresa_cliente):
        """
        POST /api/carrinho/adicionar_item/ com pacote_id → 200.
        """
        payload = {"pacote_id": pacote_surpresa_cliente.id, "quantidade": 1}

        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", payload, format="json")

        assert resposta.status_code == status.HTTP_200_OK
        assert len(resposta.data["itens"]) == 1
        assert ItemCarrinho.objects.filter(pacote=pacote_surpresa_cliente).exists()

    def test_adicionar_item_sem_produto_nem_pacote_retorna_400(self, cliente_auth):
        """
        Validação obrigatória: produto_id OU pacote_id → 400 "ID do produto ou pacote é necessário."
        """
        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", {}, format="json")

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "produto_id" in resposta.data or "error" in resposta.data

    def test_adicionar_item_quantidade_acima_estoque_retorna_400(self, cliente_auth, produto_cliente):
        """
        Regra de negócio: quantidade > item_obj.quantidade_estoque → 400 "Estoque insuficiente."
        """
        produto_cliente.quantidade_estoque = 1
        produto_cliente.save()

        payload = {"produto_id": produto_cliente.id, "quantidade": 2}

        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", payload, format="json")

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert "Estoque insuficiente" in str(resposta.data)

    def test_adicionar_item_duplicado_incrementa_quantidade(self, cliente_auth, produto_cliente):
        """
        Item existente: incrementa quantidade em vez de criar duplicata.
        """
        # Adiciona primeiro item
        cliente_auth.post("/api/carrinho/adicionar_item/", {"produto_id": produto_cliente.id, "quantidade": 1}, format="json")

        # Adiciona novamente
        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", {"produto_id": produto_cliente.id, "quantidade": 1}, format="json")

        assert resposta.status_code == status.HTTP_200_OK
        assert ItemCarrinho.objects.get(produto=produto_cliente).quantidade == 2

    def test_adicionar_item_sem_autenticacao_retorna_401(self, api_client, produto_cliente):
        """
        Permission IsAuthenticated.
        """
        resposta = api_client.post("/api/carrinho/adicionar_item/", {"produto_id": produto_cliente.id}, format="json")
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remover_item_existente_retorna_200(self, cliente_auth, item_carrinho_cliente):
        """
        POST /api/carrinho/{item_id}/remover-item/ → 200, deleta item e retorna carrinho atualizado.
        """
        resposta = cliente_auth.post(f"/api/carrinho/{item_carrinho_cliente.id}/remover-item/", format="json")

        assert resposta.status_code == status.HTTP_200_OK
        assert len(resposta.data["itens"]) == 0  # carrinho limpo
        assert not ItemCarrinho.objects.filter(id=item_carrinho_cliente.id).exists()

    def test_remover_item_inexistente_retorna_404(self, cliente_auth):
        """
        ItemCarrinho.DoesNotExist → 404 "Item não encontrado no carrinho."
        """
        resposta = cliente_auth.post("/api/carrinho/999999/remover-item/", format="json")

        assert resposta.status_code == status.HTTP_404_NOT_FOUND
        assert "Item não encontrado" in str(resposta.data)

    
    def test_remover_item_sem_autenticacao_retorna_401(self, api_client, item_carrinho_cliente):
        """
        Permission IsAuthenticated.
        """
        api_client.force_authenticate(user=None)
        resposta = api_client.post(f"/api/carrinho/{item_carrinho_cliente.id}/remover-item/", format="json")
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED

    def test_quantidade_default_um(self, cliente_auth, produto_cliente):
        """
        Omite quantidade → default 1 no ViewSet.
        """
        resposta = cliente_auth.post("/api/carrinho/adicionar_item/", {"produto_id": produto_cliente.id}, format="json")

        assert resposta.status_code == status.HTTP_200_OK
        assert ItemCarrinho.objects.get(produto=produto_cliente).quantidade == 1
