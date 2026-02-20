from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import CategoriaProduto, PacoteSurpresa, Perfil, Produto

User = get_user_model()


@pytest.fixture
def setup_dados_base():
    user_vendedor = User.objects.create_user(
        username="vendedor_user", password="password"
    )
    vendedor_perfil = Perfil.objects.create(
        usuario=user_vendedor, tipo="VENDEDOR", nome_negocio="Loja Teste"
    )

    cat_frutas = CategoriaProduto.objects.create(nome="Frutas", slug="frutas")
    cat_doces = CategoriaProduto.objects.create(nome="Doces", slug="doces")

    # Produtos
    Produto.objects.create(
        nome="Maçã",
        preco=Decimal("5.00"),
        quantidade_estoque=10,
        ativo=True,
        categoria=cat_frutas,
        vendedor=vendedor_perfil,
    )
    Produto.objects.create(
        nome="Banana",
        preco=Decimal("10.00"),
        quantidade_estoque=5,
        ativo=True,
        categoria=cat_frutas,
        vendedor=vendedor_perfil,
    )
    Produto.objects.create(
        nome="Chocolate",
        preco=Decimal("20.00"),
        quantidade_estoque=0,
        ativo=True,
        categoria=cat_doces,
        vendedor=vendedor_perfil,
    )  # Estoque 0 (deve ser excluído)
    Produto.objects.create(
        nome="Bombom",
        preco=Decimal("30.00"),
        quantidade_estoque=2,
        ativo=False,
        categoria=cat_doces,
        vendedor=vendedor_perfil,
    )  # Inativo (deve ser excluído)

    # Pacote Surpresa (Assumindo a mesma estrutura básica: nome, preco, quantidade_estoque, ativo)
    PacoteSurpresa.objects.create(
        nome="Pacote Doce",
        preco=Decimal("15.00"),
        quantidade_estoque=3,
        ativo=True,
        vendedor=vendedor_perfil,
    )
    PacoteSurpresa.objects.create(
        nome="Pacote Salgado",
        preco=Decimal("25.00"),
        quantidade_estoque=1,
        ativo=False,
        vendedor=vendedor_perfil,
    )  # Inativo (deve ser excluído)


def test_view_produtos_lista_apenas_ativos_com_estoque(client, db, setup_dados_base):
    url = reverse("core:produtos")
    response = client.get(url)

    assert response.status_code == 200

    # Produtos ficam em page_obj (paginado)
    produtos_retornados = response.context["page_obj"].object_list
    assert (
        len(produtos_retornados) == 2
    )  # Maçã e Banana (Chocolate=estoque 0, Bombom=inativo)

    nomes_produtos = {item.nome for item in produtos_retornados}
    assert "Maçã" in nomes_produtos
    assert "Banana" in nomes_produtos
    assert "Chocolate" not in nomes_produtos
    assert "Bombom" not in nomes_produtos

    # Pacotes ficam em contexto separado
    pacotes_retornados = list(response.context["pacotes"])
    assert len(pacotes_retornados) == 1  # só Pacote Doce (Pacote Salgado=inativo)

    nomes_pacotes = {p.nome for p in pacotes_retornados}
    assert "Pacote Doce" in nomes_pacotes
    assert "Pacote Salgado" not in nomes_pacotes
