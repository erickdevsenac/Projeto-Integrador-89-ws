import pytest
from core.models import Produto, CategoriaProduto, PacoteSurpresa, Perfil
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


@pytest.fixture
def setup_dados_base():
    user_vendedor = User.objects.create_user(username='vendedor_user', password='password')
    vendedor_perfil = Perfil.objects.create(usuario=user_vendedor, tipo='VENDEDOR', nome_negocio='Loja Teste')
    
    cat_frutas = CategoriaProduto.objects.create(nome='Frutas', slug='frutas')
    cat_doces = CategoriaProduto.objects.create(nome='Doces', slug='doces')

    # Produtos
    Produto.objects.create(nome='Maçã', preco=Decimal('5.00'), quantidade_estoque=10, ativo=True, categoria=cat_frutas, vendedor=vendedor_perfil)
    Produto.objects.create(nome='Banana', preco=Decimal('10.00'), quantidade_estoque=5, ativo=True, categoria=cat_frutas, vendedor=vendedor_perfil)
    Produto.objects.create(nome='Chocolate', preco=Decimal('20.00'), quantidade_estoque=0, ativo=True, categoria=cat_doces, vendedor=vendedor_perfil) # Estoque 0 (deve ser excluído)
    Produto.objects.create(nome='Bombom', preco=Decimal('30.00'), quantidade_estoque=2, ativo=False, categoria=cat_doces, vendedor=vendedor_perfil) # Inativo (deve ser excluído)

    # Pacote Surpresa (Assumindo a mesma estrutura básica: nome, preco, quantidade_estoque, ativo)
    PacoteSurpresa.objects.create(nome='Pacote Doce', preco=Decimal('15.00'), quantidade_estoque=3, ativo=True)
    PacoteSurpresa.objects.create(nome='Pacote Salgado', preco=Decimal('25.00'), quantidade_estoque=1, ativo=False) # Inativo (deve ser excluído)
    

def test_view_produtos_lista_apenas_ativos_com_estoque(client, db, setup_dados_base):
    url = reverse("core:produtos") 
    response = client.get(url)

    assert response.status_code == 200

    itens_retornados = response.context["page_obj"].object_list
    assert len(itens_retornados) == 3
    
    nomes = {item.nome for item in itens_retornados}
    assert "Maçã" in nomes
    assert "Banana" in nomes
    assert "Pacote Doce" in nomes
    assert "Chocolate" not in nomes 
    assert "Bombom" not in nomes    