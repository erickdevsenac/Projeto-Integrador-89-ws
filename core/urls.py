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
    # TODO:
    # path("sobre/", views.sobre, name="sobre"),
    # path("termos/", views.termos_uso, name="termos"),
    # path("privacidade/", views.politica_privacidade, name="privacidade"),
    # ==============================================================================
    # ROTAS DE AUTENTICAÇÃO E PERFIL
    # ==============================================================================
    # path("vendedor/", public.vendedor, name="Vendedorperfil"),
    path("vendedor/<int:usuario_id>/", public.vendedor, name="vendedor_perfil"),
    path("perfil/", perfil.perfil_detail, name="perfil"),
    path("avaliacao/", avaliacao, name="avaliacao"),
    path("nova_avaliacao/", nova_avaliacao, name="nova_avaliacao"),
    path("configuracoes/", auth.configuracoes, name="configuracoes"),
    path("logout/", auth.logout_view, name="logout"),
    path("login/", auth.login_view, name="telalogin"),
    path("cadastro/", auth.cadastro, name="cadastro"),
    path("cadastro/completar/", auth.completar_cadastro, name="completar_cadastro"),
    # Recuperação de senha
    path("alterar-senha/", auth.alterarsenha, name="alterar_senha"),
    path("recuperar-senha/", auth.recuperarsenha, name="recuperar-senha"),
    # TODO:
    # path("reset-senha/<uidb64>/<token>/", views.reset_senha, name="reset_senha"),
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
    # TODO:
    # path("categoria/<slug:categoria_slug>/", views.produtos_por_categoria, name="produtos_categoria"),
    # TODO:
    # Gestão de produtos (vendedores)
    # path("meus-produtos/", views.meus_produtos, name="meus_produtos"),
    # path("produto/<int:produto_id>/editar/", views.editar_produto, name="editar_produto"),
    # path("produto/<int:produto_id>/excluir/", views.excluir_produto, name="excluir_produto"),
    # ==============================================================================
    # ROTAS DO CARRINHO E CHECKOUT
    # ==============================================================================
    path("carrinho/", carrinho.ver_carrinho, name="ver_carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        carrinho.adicionar_carrinho,
        name="adicionar_carrinho",
    ),
    path("carrinho/atualizar/", carrinho.atualizar_carrinho, name="atualizar_carrinho"),
    path(
        "carrinho/remover/<int:produto_id>/",
        carrinho.remover_item_carrinho,
        name="remover_item_carrinho",
    ),
    # TODO:
    # path("carrinho/limpar/", views.limpar_carrinho, name="limpar_carrinho"),
    # Checkout
    path("checkout/", checkout.checkout_page, name="checkout_page"),
    path("finalizar-pedido/", checkout.finalizar_pedido, name="checkout"),
    path("aplicar-cupom/", checkout.aplicar_cupom, name="aplicar_cupom"),
    # TODO:
    # path("checkout/confirmar/", views.confirmar_pedido, name="confirmar_pedido"),
    # path("pedido/<int:pedido_id>/sucesso/", views.pedido_sucesso, name="pedido_sucesso"),
    # ==============================================================================
    # ROTAS DE PEDIDOS
    # ==============================================================================
    path("meus-pedidos/", checkout.meus_pedidos, name="meus_pedidos"),
    # TODO:
    # path("pedido/<int:pedido_id>/", views.pedido_detalhe, name="pedido_detalhe"),
    # path("pedido/<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar_pedido"),
    # path("pedido/<int:pedido_id>/avaliar/", views.avaliar_pedido, name="avaliar_pedido"),
    # TODO:
    # Gestão de pedidos (vendedores)
    # path("pedidos-recebidos/", views.pedidos_recebidos, name="pedidos_recebidos"),
    # path("sub-pedido/<int:sub_pedido_id>/", views.sub_pedido_detalhe, name="sub_pedido_detalhe"),
    # path("sub-pedido/<int:sub_pedido_id>/atualizar-status/", views.atualizar_status_pedido, name="atualizar_status_pedido"),
    # ==============================================================================
    # ROTAS DE CUPONS E PROMOÇÕES
    # ==============================================================================
    path("cupom/criar/", admin.criar_cupom, name="criar_cupom"),
    # TODO:
    # path("cupons/", views.meus_cupons, name="meus_cupons"),
    # path("cupom/<int:cupom_id>/editar/", views.editar_cupom, name="editar_cupom"),
    # ==============================================================================
    # ROTAS DE RECEITAS E CONTEÚDO
    # ==============================================================================
    path("receitas/", conteudo.receitas, name="receitas"),
    path("receita/<int:receita_id>/", conteudo.receita_detalhe, name="receita_detalhe"),
    path("receita/criar/", conteudo.cria_receita, name="criar_receita"),
    # TODO:
    # path("receita/<int:receita_id>/editar/", views.editar_receita, name="editar_receita"),
    # Conteúdo educativo
    path("dicas/", conteudo.dicas, name="dicas"),
    path("videos/", public.videos, name="videos"),
    # ==============================================================================
    # ROTAS DE ONGs E DOAÇÕES
    # ==============================================================================
    path("doacoes/", public.doacao, name="doacoes"),
    path("ong/<int:usuario_id>/", public.ongs_pagina, name="ong_pagina"),
    # TODO:
    # path("doar/<int:ong_id>/", views.fazer_doacao, name="fazer_doacao"),
    # ==============================================================================
    # ROTAS ADMINISTRATIVAS E RELATÓRIOS
    # ==============================================================================
    # TODO:
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("relatorios/", views.relatorios, name="relatorios"),
    # path("relatorio/vendas/", views.relatorio_vendas, name="relatorio_vendas"),
    # path("relatorio/produtos/", views.relatorio_produtos, name="relatorio_produtos"),
    # ==============================================================================
    # ROTAS DA EQUIPE E INSTITUCIONAL
    # ==============================================================================
    path("timedev/", public.devs, name="timedev"),
    # TODO:
    # path("equipe/", views.equipe, name="equipe"),
    # path("parceiros/", views.parceiros, name="parceiros"),
    # ==============================================================================
    # APIs AJAX E UTILITÁRIOS
    # ==============================================================================
    # TODO:
    # path("api/produtos/autocomplete/", views.api_produtos_autocomplete, name="api_produtos_autocomplete"),
    # path("api/carrinho/count/", views.api_carrinho_count, name="api_carrinho_count"),
    # path("api/cupom/aplicar/", views.api_aplicar_cupom, name="api_aplicar_cupom"),
    # path("api/cep/<str:cep>/", views.api_consultar_cep, name="api_consultar_cep"),
    # path("api/produto/<int:produto_id>/favoritar/", views.api_favoritar_produto, name="api_favoritar_produto"),
    # Notificações
    # TODO:
    # path("api/notificacoes/", views.api_notificacoes, name="api_notificacoes"),
    # path("api/notificacao/<int:notificacao_id>/marcar-lida/", views.api_marcar_notificacao_lida, name="api_marcar_notificacao_lida"),
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
