from django.conf import settings
from django.urls import path

from .views import (
    admin,
    auth,
    avaliacao,
    carrinho,
    checkout,
    conteudo,
    marketplace,
    nova_avaliacao,
    perfil,
    public,
)

app_name = "core"

urlpatterns = [
    # ==============================================================================
    # ROTAS PRINCIPAIS E NAVEGAÇÃO
    # ==============================================================================
    path("", public.index, name="index"),
    path("produtos/", marketplace.produtos, name="produtos"),
    path("contato/", public.contato, name="contato"),
    path("pacote/", marketplace.pacote, name="pacote"),
    # ==============================================================================
    # ROTAS DE AUTENTICAÇÃO E PERFIL
    # ==============================================================================
    path("vendedor/<int:usuario_id>/", public.vendedor, name="vendedor_perfil"),
    path("perfil/", perfil.perfil_detail, name="perfil"),
    path("avaliacao/", avaliacao, name="avaliacao"),
    path("nova_avaliacao/", nova_avaliacao, name="nova_avaliacao"),
    path("configuracoes/", auth.configuracoes, name="configuracoes"),
    path("logout/", auth.logout_view, name="logout"),
    path("login/", auth.login_view, name="login"),
    path("cadastro/", auth.cadastro, name="cadastro"),
    path("cadastro/completar/", auth.completar_cadastro, name="completar_cadastro"),
    path("ativar-conta/<uidb64>/<token>/", auth.ativar_conta, name="ativar_conta"),
    # Recuperação de senha
    path("alterar-senha/", auth.alterarsenha, name="alterar_senha"),
    path("recuperar-senha/", auth.recuperarsenha, name="recuperar-senha"),
    path(
        "redefinir-senha/<uidb64>/<token>/",
        auth.redefinir_senha_confirmar,
        name="password_reset_confirm",  # Nome padrão do Django
    ),
    # ==============================================================================
    # ROTAS DE PRODUTOS E MARKETPLACE
    # ==============================================================================
    # As rotas de "produtos" e "busca" já foram declaradas na seção principal
    path(
        "produto/<int:produto_id>/", marketplace.produto_detalhe, name="produto_detalhe"
    ),
    path(
        "produto/<int:produto_id>/quick-view/",
        marketplace.produto_quick_view,
        name="produto_quick_view",
    ),
    path("produto/cadastrar/", marketplace.cadastrar_produto, name="cadastrar_produto"),
    path("pacote/", public.pacote_detalhe, name="pacote_detalhe"),
    path("pacote/<int:pacote_id>/", public.pacote_detalhe, name="pacote_detalhe"),
    path(
        "editar_produto/<int:produto_id>/",
        marketplace.editar_produto,
        name="editar_produto",
    ),
    path(
        "excluir_produto/<int:produto_id>/",
        marketplace.excluir_produto,
        name="excluir_produto",
    ),
    path("editar_produto", marketplace.editar_produto, name="editar_produto"),
    path(
        "pacote/editar/<int:pacote_id>/",
        marketplace.editar_pacote,
        name="editar_pacote",
    ),
    path(
        "pacote/excluir/<int:pacote_id>/",
        marketplace.excluir_pacote,
        name="excluir_pacote",
    ),
    # ==============================================================================
    # ROTAS DO CARRINHO E CHECKOUT
    # ==============================================================================
    path("carrinho/", carrinho.ver_carrinho, name="ver_carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        carrinho.adicionar_carrinho,
        name="adicionar_carrinho",
    ),
    path(
        "carrinho/atualizar/",
        carrinho.atualizar_carrinho,
        name="atualizar_carrinho_ajax",
    ),
    path(
        "carrinho/remover/",
        carrinho.remover_item_carrinho,
        name="remover_carrinho_ajax",
    ),
    path(
        "carrinho/adicionar_pacote/<int:pacote_id>/",
        carrinho.adicionar_pacote_carrinho,
        name="adicionar_pacote_carrinho",
    ),
    # Checkout
    path("checkout/", checkout.checkout_page, name="checkout_page"),
    path("finalizar-pedido/", checkout.finalizar_pedido, name="finalizar_pedido"),
    path("aplicar-cupom/", checkout.aplicar_cupom, name="aplicar_cupom"),
    # ==============================================================================
    # ROTAS DE PEDIDOS
    # ==============================================================================
    path("meus-pedidos/", checkout.meus_pedidos, name="meus_pedidos"),
    path(
        "vendedor/pedidos/",
        checkout.painel_pedidos_vendedor,
        name="painel_pedidos_vendedor",
    ),
    # ==============================================================================
    # ROTAS DE CUPONS E PROMOÇÕES
    # ==============================================================================
    path("cupom/criar/", admin.criar_cupom, name="criar_cupom"),
    # ==============================================================================
    # ROTAS DE RECEITAS E CONTEÚDO
    # ==============================================================================
    path("receitas/", conteudo.receitas, name="receitas"),
    path("receita/<int:receita_id>/", conteudo.receita_detalhe, name="receita_detalhe"),
    path("receita/criar/", conteudo.cria_receita, name="criar_receita"),
    # Conteúdo educativo
    path("dicas/", conteudo.dicas, name="dicas"),
    path("dicas-detalhes/<int:id>/", conteudo.detalhes_dica, name="dicas_detalhes"),
    path("videos/", public.videos, name="videos"),
    # ==============================================================================
    # ROTAS DE ONGs E DOAÇÕES
    # ==============================================================================
    path("doacoes/", public.doacao, name="doacoes"),
    path("ong/<int:usuario_id>/", public.ongs_pagina, name="ong_pagina"),
    # ==============================================================================
    # ROTAS ADMINISTRATIVAS E RELATÓRIOS
    # ==============================================================================
    path("timedev/", public.devs, name="timedev"),
]

# Adiciona rotas de debug apenas se DEBUG=True
if settings.DEBUG:
    urlpatterns += [
        path("debug/email-test/", admin.debug_email_test, name="debug_email_test"),
        path("debug/cache-clear/", admin.debug_cache_clear, name="debug_cache_clear"),
        path(
            "debug/session-info/", admin.debug_session_info, name="debug_session_info"
        ),
    ]
