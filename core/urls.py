from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = "core"

urlpatterns = [
    # ==============================================================================
    # ROTAS PRINCIPAIS E NAVEGAÇÃO
    # ==============================================================================
    path("", views.index, name="index"),
    path("produtos/", views.produtos, name="produtos"),
    path("busca/", views.buscar_produtos, name="buscar_produtos"),
    path("contato/", views.contato, name="contato"),
    #TODO:
    # path("sobre/", views.sobre, name="sobre"),
    # path("termos/", views.termos_uso, name="termos"),
    # path("privacidade/", views.politica_privacidade, name="privacidade"),

    # ==============================================================================
    # ROTAS DE AUTENTICAÇÃO E PERFIL
    # ==============================================================================
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login_view, name="telalogin"),  
    path("logout/", views.logout_view, name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),

    # Recuperação de senha
    path("alterar-senha/", views.alterarsenha, name="alterar_senha"),  
    path("recuperar-senha/", views.recuperarsenha, name="recuperar-senha"),
    path("vendedor/", views.vendedor, name="Vendedorperfil"),
    path('avaliacao/', views.avaliacao, name='avaliacao'), 
    path('nova_avaliacao/', views.nova_avaliacao, name='nova_avaliacao'),  


    #TODO:
    # path("reset-senha/<uidb64>/<token>/", views.reset_senha, name="reset_senha"),

    # ==============================================================================
    # ROTAS DE PRODUTOS E MARKETPLACE
    # ==============================================================================

 path("produtos/", views.produtos, name="produtos"),
    path("busca/", views.buscar_produtos, name="buscar_produtos"),
    #TODO:
    # path("produto/<int:produto_id>/", views.produto_detalhe, name="produto_detalhe"),
    # path("categoria/<slug:categoria_slug>/", views.produtos_por_categoria, name="produtos_categoria"),
    
    #TODO:
    # Gestão de produtos (vendedores)
    # path("meus-produtos/", views.meus_produtos, name="meus_produtos"),
    # path("produto/cadastrar/", views.cadastrar_produto, name="cadastrar_produto"),
    # path("produto/<int:produto_id>/editar/", views.editar_produto, name="editar_produto"),
    # path("produto/<int:produto_id>/excluir/", views.excluir_produto, name="excluir_produto"),
    
    # ==============================================================================
    # ROTAS DO CARRINHO E CHECKOUT
    # ==============================================================================
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.adicionar_carrinho, name="adicionar_carrinho"),
    path("carrinho/atualizar/", views.atualizar_carrinho, name="atualizar_carrinho"),
    #TODO:
    # path("carrinho/remover/<int:produto_id>/", views.remover_item_carrinho, name="remover_item_carrinho"),
    # path("carrinho/limpar/", views.limpar_carrinho, name="limpar_carrinho"),
    
    # Checkout
    path("checkout/", views.finalizar_pedido, name="checkout"),
    #TODO:
    # path("checkout/confirmar/", views.confirmar_pedido, name="confirmar_pedido"),
    # path("pedido/<int:pedido_id>/sucesso/", views.pedido_sucesso, name="pedido_sucesso"),
    
    # ==============================================================================
    # ROTAS DE PEDIDOS
    # ==============================================================================
    path("meus-pedidos/", views.meus_pedidos, name="meus_pedidos"),
    #TODO:
    # path("pedido/<int:pedido_id>/", views.pedido_detalhe, name="pedido_detalhe"),
    # path("pedido/<int:pedido_id>/cancelar/", views.cancelar_pedido, name="cancelar_pedido"),
    # path("pedido/<int:pedido_id>/avaliar/", views.avaliar_pedido, name="avaliar_pedido"),
    
    #TODO:
    # Gestão de pedidos (vendedores)
    # path("pedidos-recebidos/", views.pedidos_recebidos, name="pedidos_recebidos"),
    # path("sub-pedido/<int:sub_pedido_id>/", views.sub_pedido_detalhe, name="sub_pedido_detalhe"),
    # path("sub-pedido/<int:sub_pedido_id>/atualizar-status/", views.atualizar_status_pedido, name="atualizar_status_pedido"),
    
    # ==============================================================================
    # ROTAS DE CUPONS E PROMOÇÕES
    # ==============================================================================
    path("cupom/criar/", views.criar_cupom, name="criar_cupom"),
    #TODO:
    # path("cupons/", views.meus_cupons, name="meus_cupons"),
    # path("cupom/<int:cupom_id>/editar/", views.editar_cupom, name="editar_cupom"),
    
    # ==============================================================================
    # ROTAS DE RECEITAS E CONTEÚDO
    # ==============================================================================
    path("receitas/", views.receitas, name="receitas"),
    path("receita/<int:receita_id>/", views.receita_detalhe, name="receita_detalhe"),
    #TODO:
    # path("receita/criar/", views.criar_receita, name="criar_receita"),
    # path("receita/<int:receita_id>/editar/", views.editar_receita, name="editar_receita"),
    
    # Conteúdo educativo
    path("dicas/", views.dicas, name="dicas"),
    path("videos/", views.videos, name="videos"),
    
    # ==============================================================================
    # ROTAS DE ONGs E DOAÇÕES
    # ==============================================================================
    #TODO:
    # path("doacoes/", views.doacoes, name="doacoes"),
    # path("ong/<int:usuario_id>/", views.ong_pagina, name="ong_pagina"),
    # path("doar/<int:ong_id>/", views.fazer_doacao, name="fazer_doacao"),
    
    # ==============================================================================
    # ROTAS ADMINISTRATIVAS E RELATÓRIOS
    # ==============================================================================
    #TODO:
    # path("dashboard/", views.dashboard, name="dashboard"),
    # path("relatorios/", views.relatorios, name="relatorios"),
    # path("relatorio/vendas/", views.relatorio_vendas, name="relatorio_vendas"),
    # path("relatorio/produtos/", views.relatorio_produtos, name="relatorio_produtos"),
    
    # ==============================================================================
    # ROTAS DA EQUIPE E INSTITUCIONAL
    # ==============================================================================
    path("timedev/", views.devs, name="timedev"),
    #TODO:
    # path("equipe/", views.equipe, name="equipe"),
    # path("parceiros/", views.parceiros, name="parceiros"),
    
    # ==============================================================================
    # APIs AJAX E UTILITÁRIOS
    # ==============================================================================
    #TODO:
    # path("api/produtos/autocomplete/", views.api_produtos_autocomplete, name="api_produtos_autocomplete"),
    # path("api/carrinho/count/", views.api_carrinho_count, name="api_carrinho_count"),
    # path("api/cupom/aplicar/", views.api_aplicar_cupom, name="api_aplicar_cupom"),
    # path("api/cep/<str:cep>/", views.api_consultar_cep, name="api_consultar_cep"),
    # path("api/produto/<int:produto_id>/favoritar/", views.api_favoritar_produto, name="api_favoritar_produto"),
    
    # Notificações
    #TODO:
    # path("api/notificacoes/", views.api_notificacoes, name="api_notificacoes"),
    # path("api/notificacao/<int:notificacao_id>/marcar-lida/", views.api_marcar_notificacao_lida, name="api_marcar_notificacao_lida"),
    
    
    # ==============================================================================
    # ROTAS DE WEBHOOKS E INTEGRAÇÕES
    # ==============================================================================
    #TODO:
    # path("webhook/pagamento/", views.webhook_pagamento, name="webhook_pagamento"),
    # path("webhook/correios/", views.webhook_correios, name="webhook_correios"),
    
    # ==============================================================================
    # ROTAS DE AVALIAÇÕES E FEEDBACK
    # ==============================================================================
    #TODO:
    # path("produto/<int:produto_id>/avaliar/", views.avaliar_produto, name="avaliar_produto"),
    # path("vendedor/<int:vendedor_id>/avaliar/", views.avaliar_vendedor, name="avaliar_vendedor"),
    # path("avaliacoes/", views.minhas_avaliacoes, name="minhas_avaliacoes"),
    
    # ==============================================================================
    # ROTAS DE FAVORITOS E LISTAS
    # ==============================================================================
    #TODO:
    # path("favoritos/", views.meus_favoritos, name="meus_favoritos"),
    # path("lista-desejos/", views.lista_desejos, name="lista_desejos"),
    # path("produto/<int:produto_id>/favoritar/", views.favoritar_produto, name="favoritar_produto"),
    
    # ==============================================================================
    # ROTAS DE CHAT E SUPORTE
    # ==============================================================================
    #TODO:
    # path("chat/", views.chat_suporte, name="chat_suporte"),
    # path("chat/<int:conversa_id>/", views.chat_conversa, name="chat_conversa"),
    # path("faq/", views.faq, name="faq"),
    # path("suporte/", views.suporte, name="suporte"),
    
    # ==============================================================================
    # ROTAS DE GAMIFICAÇÃO E PONTOS
    # ==============================================================================
    #TODO:
    # path("pontos/", views.meus_pontos, name="meus_pontos"),
    # path("ranking/", views.ranking_usuarios, name="ranking_usuarios"),
    # path("conquistas/", views.minhas_conquistas, name="minhas_conquistas"),
    
    # ==============================================================================
    # ROTAS DE CONFIGURAÇÕES AVANÇADAS
    # ==============================================================================
    #TODO:
    # path("configuracoes/notificacoes/", views.configurar_notificacoes, name="configurar_notificacoes"),
    # path("configuracoes/privacidade/", views.configurar_privacidade, name="configurar_privacidade"),
    # path("configuracoes/conta/", views.configurar_conta, name="configurar_conta"),
    
    # Exportação de dados
    #TODO:
    # path("exportar/dados/", views.exportar_dados_usuario, name="exportar_dados"),
    # path("excluir/conta/", views.excluir_conta, name="excluir_conta"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += [
        path("debug/email-test/", views.debug_email_test, name="debug_email_test"),
        path("debug/cache-clear/", views.debug_cache_clear, name="debug_cache_clear"),
        path("debug/session-info/", views.debug_session_info, name="debug_session_info"),
    ]



    # # ==============================================================================
    # # ROTAS DA API REST
    # # ==============================================================================
    # path("api/v1/", include(router.urls)),
    # path("api/v1/auth/", include('rest_framework.urls')),
    
    # # Endpoints customizados da API
    # path("api/v1/carrinho/", views.api_carrinho, name="api_carrinho"),
    # path("api/v1/checkout/", views.api_checkout, name="api_checkout"),
    # path("api/v1/produtos/buscar/", views.api_buscar_produtos, name="api_buscar_produtos"),
    # path("api/v1/estatisticas/", views.api_estatisticas, name="api_estatisticas"),