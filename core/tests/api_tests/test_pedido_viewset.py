"""
Sprint 3 — Testes do PedidoViewSet
===================================
Coberturas:
  - POST /api/pedido/ (create) — carrinho válido, vazio, sem carrinho, não autenticado
  - GET  /api/pedido/ (list)   — isolamento por cliente
  - GET  /api/pedido/{id}/ (retrieve) — 404 para pedido de outro usuário

Dependências confirmadas via leitura dos models:
  - Perfil: fields obrigatórios (endereco, cep, cidade, estado, nome_completo / nome_negocio)
  - Carrinho: OneToOneField -> Perfil (related_name='carrinho')
  - ItemCarrinho: FK -> Carrinho, FK -> Produto ou PacoteSurpresa
  - Produto: campos obrigatórios (preco, nome, quantidade_estoque, tipo_quantidade, vendedor)
  - Pedido.save(): calcula valor_total automaticamente via override

Notas de contrato:
  - Pedido.valor_frete e valor_desconto default=0.00 → valor_total = valor_produtos
  - endereco_entrega: usa request.data ou fallback para perfil.endereco
  - forma_pagamento: usa request.data ou default "PIX"
  - Estoque é debitado inline (sem validação de estoque insuficiente no ViewSet — bug a monitorar)
  - Carrinho limpo via carrinho.itens.all().delete() ao final do create()
"""

import pytest
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APIClient

from core.models import Pedido, PedidoVendedor, ItemPedido
from core.models.carrinho import Carrinho, ItemCarrinho
from core.models.produto import Produto, PacoteSurpresa
from core.models.perfil import Perfil


# ---------------------------------------------------------------------------
# Helpers / Fixtures reutilizáveis
# ---------------------------------------------------------------------------

def _criar_user_e_perfil(
    username: str,
    tipo: str,
    nome_completo: str = "",
    nome_negocio: str = "",
    password: str = "senha@123",
) -> tuple[User, Perfil]:
    """
    Cria User + Perfil com campos obrigatórios preenchidos.
    Mantém inline para evitar dependência de fixtures globais instáveis.
    """
    user = User.objects.create_user(username=username, password=password)
    perfil = Perfil.objects.create(
        usuario=user,
        tipo=tipo,
        nome_completo=nome_completo,
        nome_negocio=nome_negocio,
        endereco="Rua Teste, 123",
        cep="79800000",
        cidade="Dourados",
        estado="MS",
        # Campos de ONG/Vendedor — preenchidos com defaults vazios quando não aplicável
        descricao_parceiro="",
        objetivo="",
        imagem_carrossel1="",
        imagem_carrossel2="",
        imagem_carrossel3="",
    )
    return user, perfil


def _criar_produto(vendedor_perfil: Perfil, preco: Decimal = Decimal("10.00"), estoque: int = 10) -> Produto:
    """Cria produto vinculado a um vendedor, com campos obrigatórios mínimos."""
    return Produto.objects.create(
        vendedor=vendedor_perfil,
        nome=f"Produto de {vendedor_perfil.nome_negocio or vendedor_perfil.usuario.username}",
        preco=preco,
        quantidade_estoque=estoque,
        tipo_quantidade="QUANTIA",  # choices: PESA / MEDE / QUANTIA
        descricao="Produto de teste",
    )


def _criar_carrinho_com_item(
    cliente_perfil: Perfil,
    produto: Produto,
    quantidade: int = 2,
) -> tuple[Carrinho, ItemCarrinho]:
    """Cria (ou recupera) um Carrinho para o cliente e adiciona um ItemCarrinho."""
    carrinho, _ = Carrinho.objects.get_or_create(usuario=cliente_perfil)
    item = ItemCarrinho.objects.create(
        carrinho=carrinho,
        produto=produto,
        quantidade=quantidade,
    )
    return carrinho, item


# ---------------------------------------------------------------------------
# Fixtures pytest
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def cliente(db):
    """Perfil CLIENTE com carrinho vazio (sem itens)."""
    _, perfil = _criar_user_e_perfil(
        username="cliente_teste",
        tipo="CLIENTE",
        nome_completo="Cliente Teste",
    )
    return perfil


@pytest.fixture
def vendedor(db):
    """Perfil VENDEDOR."""
    _, perfil = _criar_user_e_perfil(
        username="vendedor_teste",
        tipo="VENDEDOR",
        nome_negocio="Loja Verde",
    )
    return perfil


@pytest.fixture
def vendedor2(db):
    """Segundo VENDEDOR para testes de multi-subpedido."""
    _, perfil = _criar_user_e_perfil(
        username="vendedor2_teste",
        tipo="VENDEDOR",
        nome_negocio="Loja Azul",
    )
    return perfil


@pytest.fixture
def produto(db, vendedor):
    return _criar_produto(vendedor, preco=Decimal("20.00"), estoque=10)


@pytest.fixture
def produto_vendedor2(db, vendedor2):
    return _criar_produto(vendedor2, preco=Decimal("15.00"), estoque=5)


@pytest.fixture
def cliente_autenticado(api_client, cliente):
    """Retorna APIClient já autenticado como 'cliente'."""
    api_client.force_authenticate(user=cliente.usuario)
    return api_client


PEDIDO_URL = "/api/pedido/"


# ---------------------------------------------------------------------------
# POST /api/pedido/ — autenticação
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPedidoAutenticacao:

    def test_create_sem_autenticacao_retorna_401(self, api_client):
        """
        Endpoint exige IsAuthenticated — request anônimo deve retornar 401.
        Valida que a permission_class está corretamente configurada no ViewSet.
        """
        response = api_client.post(PEDIDO_URL, {}, format="json")
        assert response.status_code == 401

    def test_list_sem_autenticacao_retorna_401(self, api_client):
        response = api_client.get(PEDIDO_URL)
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/pedido/ — fluxo happy path
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPedidoCreate:

    def test_create_carrinho_valido_retorna_201(self, cliente_autenticado, cliente, produto):
        """
        Fluxo completo: cliente com carrinho populado → POST → 201.
        Verifica criação de Pedido, PedidoVendedor e ItemPedido.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=2)

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert response.status_code == 201, response.data

    def test_create_gera_pedido_principal(self, cliente_autenticado, cliente, produto):
        """Após POST bem-sucedido, um Pedido deve existir vinculado ao cliente."""
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert Pedido.objects.filter(cliente=cliente).count() == 1

    def test_create_gera_subpedido_por_vendedor(self, cliente_autenticado, cliente, produto):
        """
        Um item de um vendedor deve gerar exatamente um PedidoVendedor.
        Contrato: agrupamento por 'vendedor' do produto.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        assert pedido.sub_pedidos.count() == 1
        sub = pedido.sub_pedidos.first()
        assert sub.vendedor == produto.vendedor

    def test_create_dois_vendedores_geram_dois_subpedidos(
        self, cliente_autenticado, cliente, produto, produto_vendedor2
    ):
        """
        Itens de dois vendedores distintos devem gerar dois PedidoVendedor.
        Valida a lógica de agrupamento por vendedor no create().
        """
        carrinho, _ = Carrinho.objects.get_or_create(usuario=cliente)
        ItemCarrinho.objects.create(carrinho=carrinho, produto=produto, quantidade=1)
        ItemCarrinho.objects.create(carrinho=carrinho, produto=produto_vendedor2, quantidade=1)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        assert pedido.sub_pedidos.count() == 2

    def test_create_gera_item_pedido_por_item_carrinho(self, cliente_autenticado, cliente, produto):
        """
        Cada ItemCarrinho deve resultar em um ItemPedido com snapshot de preco_unitario.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=3)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        sub = pedido.sub_pedidos.first()
        itens = sub.itens.all()
        assert itens.count() == 1
        item = itens.first()
        assert item.quantidade == 3
        assert item.preco_unitario == produto.preco

    def test_create_debita_estoque_do_produto(self, cliente_autenticado, cliente, produto):
        """
        Side effect crítico: estoque deve ser decrementado pela quantidade comprada.
        Race condition (sem SELECT FOR UPDATE) é um débito técnico — monitorar.
        """
        estoque_inicial = produto.quantidade_estoque
        quantidade_comprada = 3
        _criar_carrinho_com_item(cliente, produto, quantidade=quantidade_comprada)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        produto.refresh_from_db()
        assert produto.quantidade_estoque == estoque_inicial - quantidade_comprada

    def test_create_limpa_itens_do_carrinho(self, cliente_autenticado, cliente, produto):
        """
        Após checkout bem-sucedido, carrinho.itens deve estar vazio.
        Confirma que o delete() foi executado no final do create().
        """
        carrinho, _ = _criar_carrinho_com_item(cliente, produto, quantidade=1)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert ItemCarrinho.objects.filter(carrinho=carrinho).count() == 0

    def test_create_valor_total_calculado_corretamente(self, cliente_autenticado, cliente, produto):
        """
        valor_total = valor_produtos + valor_frete(0) - valor_desconto(0).
        Valida o override de Pedido.save() com os defaults do ViewSet.
        """
        quantidade = 2
        _criar_carrinho_com_item(cliente, produto, quantidade=quantidade)
        esperado = produto.preco * quantidade

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        assert pedido.valor_total == esperado

    def test_create_endereco_entrega_usa_perfil_quando_nao_informado(
        self, cliente_autenticado, cliente, produto
    ):
        """
        Sem 'endereco_entrega' no payload, deve usar cliente_perfil.endereco (fallback).
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        assert pedido.endereco_entrega == cliente.endereco

    def test_create_forma_pagamento_custom_no_payload(self, cliente_autenticado, cliente, produto):
        """
        Quando 'forma_pagamento' é informado no payload, deve ser persistido no Pedido.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        cliente_autenticado.post(
            PEDIDO_URL,
            {"forma_pagamento": "BOLETO"},
            format="json",
        )

        pedido = Pedido.objects.get(cliente=cliente)
        assert pedido.forma_pagamento == "BOLETO"

    def test_create_resposta_inclui_numero_pedido(self, cliente_autenticado, cliente, produto):
        """
        O response body deve conter o número do pedido gerado (campo 'numero_pedido').
        Valida contrato do PedidoSerializer.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert "numero_pedido" in response.data
        assert response.data["numero_pedido"].startswith("PED-")

    def test_double_submit_segundo_post_retorna_400_carrinho_vazio(
        self, cliente_autenticado, cliente, produto
    ):
        """
        Proteção contra double-submit: após o primeiro POST bem-sucedido,
        o carrinho é limpo. Um segundo POST imediato deve retornar 400.
        Garante que não há debit duplo de estoque por race condition de UI.
        """
        _criar_carrinho_com_item(cliente, produto, quantidade=1)

        r1 = cliente_autenticado.post(PEDIDO_URL, {}, format="json")
        assert r1.status_code == 201

        # Segundo POST — carrinho já vazio após o primeiro checkout
        r2 = cliente_autenticado.post(PEDIDO_URL, {}, format="json")
        assert r2.status_code == 400
        assert "error" in r2.data

    def test_multi_vendedor_valor_subtotal_por_subpedido(
        self, cliente_autenticado, cliente, produto, produto_vendedor2
    ):
        """
        Cada PedidoVendedor.valor_subtotal deve refletir apenas os itens
        daquele vendedor — não o total do pedido principal.
        Valida a lógica de acumulação de 'dados["subtotal"]' no create().
        """
        carrinho, _ = Carrinho.objects.get_or_create(usuario=cliente)
        qtd_v1, qtd_v2 = 2, 3
        ItemCarrinho.objects.create(carrinho=carrinho, produto=produto, quantidade=qtd_v1)
        ItemCarrinho.objects.create(carrinho=carrinho, produto=produto_vendedor2, quantidade=qtd_v2)

        cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        pedido = Pedido.objects.get(cliente=cliente)
        sub_v1 = pedido.sub_pedidos.get(vendedor=produto.vendedor)
        sub_v2 = pedido.sub_pedidos.get(vendedor=produto_vendedor2.vendedor)

        assert sub_v1.valor_subtotal == produto.preco * qtd_v1
        assert sub_v2.valor_subtotal == produto_vendedor2.preco * qtd_v2


# ---------------------------------------------------------------------------
# POST /api/pedido/ — cenários de erro (carrinho inválido)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPedidoCreateErros:

    def test_create_carrinho_vazio_retorna_400(self, cliente_autenticado, cliente):
        """
        Carrinho existe mas sem itens → deve retornar 400 com mensagem 'Carrinho vazio.'
        """
        Carrinho.objects.create(usuario=cliente)  # Carrinho sem itens

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    def test_create_sem_carrinho_retorna_400(self, cliente_autenticado, cliente):
        """
        Cliente sem Carrinho cadastrado → DoesNotExist → deve retornar 400.
        Garante que o except Carrinho.DoesNotExist está sendo tratado corretamente.
        """
        # Não cria Carrinho — Perfil sem related object
        assert not Carrinho.objects.filter(usuario=cliente).exists()

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    def test_create_estoque_insuficiente_expoe_bug_sem_validacao(
    self, cliente_autenticado, cliente, produto
):
        """
        BUG DOCUMENTADO: o ViewSet não valida estoque antes de debitar.
        Se quantidade_comprada > quantidade_estoque, o PositiveIntegerField
        pode ir a negativo (SQLite) ou lançar IntegrityError (PostgreSQL).

        Este teste DEVE FALHAR com IntegrityError ou retornar 500 até que
        a validação seja implementada no create():

            if item_obj.quantidade_estoque < item_carrinho.quantidade:
                raise ValidationError("Estoque insuficiente para: ...")

        Marcar com xfail enquanto o bug não for corrigido.
        """
        produto.quantidade_estoque = 1
        produto.save()

        _criar_carrinho_com_item(cliente, produto, quantidade=5)  # > estoque

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        # Comportamento ESPERADO após correção:
        assert response.status_code == 400, (
            f"BUG ATIVO: ViewSet aceitou pedido com estoque insuficiente. "
            f"status={response.status_code}"
        )

    def test_create_estoque_insuficiente_retorna_400(self, cliente_autenticado, cliente, produto):
        """
        Validação de estoque na pré-passagem: quantidade_comprada > quantidade_estoque
        deve retornar 400 com campo 'detalhes' identificando o produto.
        Garante que nenhum Pedido/PedidoVendedor/ItemPedido é criado.
        """
        produto.quantidade_estoque = 1
        produto.save()

        _criar_carrinho_com_item(cliente, produto, quantidade=5)

        response = cliente_autenticado.post(PEDIDO_URL, {}, format="json")

        assert response.status_code == 400
        assert "error" in response.data
        assert "detalhes" in response.data
        assert any(produto.nome.lower() in d.lower() for d in response.data["detalhes"])
        # Nenhum pedido deve ter sido criado — atomic garantiu rollback total
        assert Pedido.objects.filter(cliente=cliente).count() == 0


# ---------------------------------------------------------------------------
# GET /api/pedido/ — isolamento de lista
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPedidoList:

    def _extrair_results(self, response) -> list:
        """
        Helper interno: normaliza a resposta paginada do DRF.
        settings.py define DEFAULT_PAGINATION_CLASS=PageNumberPagination,
        logo response.data SEMPRE é {"count": N, "next": ..., "results": [...]}.
        Nunca iterar diretamente sobre response.data em list endpoints.
        """
        assert "results" in response.data, (
            f"Response não é paginada como esperado. data={response.data}"
        )
        return response.data["results"]

    def test_list_retorna_apenas_pedidos_do_cliente_autenticado(
        self, api_client, cliente, vendedor, produto
    ):
        """
        get_queryset() filtra por cliente=request.user.perfil.
        Pedidos de outro cliente NÃO devem aparecer na listagem.
        """
        # Cria pedido para o cliente principal
        _criar_carrinho_com_item(cliente, produto, quantidade=1)
        api_client.force_authenticate(user=cliente.usuario)
        api_client.post(PEDIDO_URL, {}, format="json")

        # Cria um segundo cliente com pedido próprio
        _, cliente2 = _criar_user_e_perfil(
            username="cliente2_isolamento",
            tipo="CLIENTE",
            nome_completo="Cliente Dois",
        )
        produto2 = _criar_produto(vendedor, preco=Decimal("5.00"), estoque=5)
        _criar_carrinho_com_item(cliente2, produto2, quantidade=1)
        api_client.force_authenticate(user=cliente2.usuario)
        api_client.post(PEDIDO_URL, {}, format="json")

        # Autentica de volta como cliente1 e verifica isolamento
        api_client.force_authenticate(user=cliente.usuario)
        response = api_client.get(PEDIDO_URL)

        assert response.status_code == 200

        # ✅ FIX: acessar .data["results"] — não iterar sobre .data diretamente
        results = self._extrair_results(response)
        ids_retornados = [p["id"] for p in results]

        pedidos_cliente1 = Pedido.objects.filter(cliente=cliente)
        pedidos_cliente2 = Pedido.objects.filter(cliente=cliente2)

        for pedido in pedidos_cliente1:
            assert pedido.id in ids_retornados, (
                f"Pedido {pedido.id} do próprio cliente não apareceu na lista"
            )

        for pedido in pedidos_cliente2:
            assert pedido.id not in ids_retornados, (
                f"VAZAMENTO DE ISOLAMENTO: Pedido {pedido.id} de outro cliente retornou na lista"
            )

    def test_list_cliente_sem_pedidos_retorna_lista_vazia(self, cliente_autenticado):
        """
        Cliente autenticado sem pedidos deve receber estrutura paginada com results vazio.
        """
        response = cliente_autenticado.get(PEDIDO_URL)

        assert response.status_code == 200

        # ✅ FIX: estrutura paginada — count=0, results=[]
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_retorna_estrutura_paginada(self, cliente_autenticado):
        """
        Smoke test: valida que o contrato de paginação está presente.
        Previne regressão caso alguém remova a pagination_class global.
        """
        response = cliente_autenticado.get(PEDIDO_URL)

        assert response.status_code == 200
        assert "count" in response.data
        assert "results" in response.data
        assert "next" in response.data
        assert "previous" in response.data

# ---------------------------------------------------------------------------
# GET /api/pedido/{id}/ — isolamento de retrieve
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPedidoRetrieve:

    def test_retrieve_pedido_proprio_retorna_200(
        self, api_client, cliente, vendedor, produto
    ):
        """Cliente pode acessar o próprio pedido via GET /api/pedido/{id}/."""
        _criar_carrinho_com_item(cliente, produto, quantidade=1)
        api_client.force_authenticate(user=cliente.usuario)
        create_response = api_client.post(PEDIDO_URL, {}, format="json")
        pedido_id = create_response.data["id"]

        response = api_client.get(f"{PEDIDO_URL}{pedido_id}/")

        assert response.status_code == 200
        assert response.data["id"] == pedido_id

    def test_retrieve_pedido_de_outro_usuario_retorna_404(
        self, api_client, cliente, vendedor, produto
    ):
        """
        Isolamento via get_queryset(): o DRF usa get_queryset() no get_object(),
        então pedidos de outros clientes resultam em 404 (não 403).
        Comportamento correto — sem information leak de IDs alheios.
        """
        # Cria pedido para cliente1
        _criar_carrinho_com_item(cliente, produto, quantidade=1)
        api_client.force_authenticate(user=cliente.usuario)
        create_response = api_client.post(PEDIDO_URL, {}, format="json")
        pedido_id_cliente1 = create_response.data["id"]

        # Autentica como cliente2 e tenta acessar o pedido do cliente1
        _, cliente2 = _criar_user_e_perfil(
            username="cliente2_retrieve",
            tipo="CLIENTE",
            nome_completo="Cliente Dois Retrieve",
        )
        api_client.force_authenticate(user=cliente2.usuario)
        response = api_client.get(f"{PEDIDO_URL}{pedido_id_cliente1}/")

        assert response.status_code == 404

    def test_retrieve_sem_autenticacao_retorna_401(self, api_client):
        """Retrieve sem token deve retornar 401 antes mesmo de buscar o objeto."""
        response = api_client.get(f"{PEDIDO_URL}9999/")
        assert response.status_code == 401
