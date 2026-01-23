from core.models.produto import Produto,PacoteSurpresa
import pytest

@pytest.mark.django_db
class TestProdutoModel:
    def test_deve_verificar_se_produtos_com_valor_negativo_podem_ser_comprados(self, vendedor_fake):

        # ARRANGE
        produto = Produto.objects.create(
            vendedor=vendedor_fake,
            nome="Banana Nanica",
            preco=-1.00,
            quantidade_estoque=1,
            ativo=True
        )

        # ACT & ASSERT
        assert produto.valor_negativo is False

    def test_deve_verificar_se_o_vendedor_e_um_vendedor_se_nao_for_nao_deixar_cadastrar_produto(self, cliente_fake):

        # ARRANGE
        produto = Produto.objects.create(
            vendedor=cliente_fake,
            nome="Limão Siciliano ",
            preco=1.00,
            quantidade_estoque=1,
            ativo=True
        )

        # ACT & ASSERT
        assert produto.verifica_vendedor is False

    def test_deve_verificar_se_o_pacote_surpresa_deletado_foi_deletado_do_banco_de_dados(self, vendedor_fake):
        # ARRANGE
        pacote = PacoteSurpresa.objects.create(
            vendedor=vendedor_fake,
            nome="Dodos assados",
            descricao="comidinhas",
            preco=1.00,
            quantidade_estoque=1,
            ativo=True
        )

        pacote.delete()
        # ACT & ASSERT
        assert PacoteSurpresa.objects.filter(id=pacote.id).exists() is False
