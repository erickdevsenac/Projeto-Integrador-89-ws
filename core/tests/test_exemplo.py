import pytest
from core.models.produto import Produto

@pytest.mark.django_db
class TestProdutoModel:
    
    def test_produto_deve_estar_disponivel_com_estoque_e_ativo(self, vendedor_fake):
        """
        Testa se o produto fica disponível quando tudo está correto.
        """
        # ARRANGE: O 'vendedor_fake' vem do conftest.py automaticamente
        produto = Produto.objects.create(
            vendedor=vendedor_fake,
            nome="Notebook Gamer",
            preco=5000.00,
            quantidade_estoque=10,
            ativo=True
        )

        # ACT & ASSERT
        assert produto.disponivel_para_venda is True

    def test_produto_nao_deve_estar_disponivel_sem_estoque(self, vendedor_fake):
        """
        Testa se o produto fica indisponível com estoque zero.
        """
        produto = Produto.objects.create(
            vendedor=vendedor_fake,
            nome="Mouse Quebrado",
            preco=50.00,
            quantidade_estoque=0,
            ativo=True
        )
        assert produto.disponivel_para_venda is False