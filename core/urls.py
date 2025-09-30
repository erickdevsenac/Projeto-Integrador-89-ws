from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = "core"

urlpatterns = [
    # Rotas Principais
    path("", views.index, name="index"),
    path("produtos/", views.produtos, name="produtos"),
    path("busca/", views.buscar_produtos, name="buscar_produtos"),
    path("contato/", views.contato, name="contato"),
  
    # Rotas de Autenticação e Usuário
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login_view, name="telalogin"),  
    path("logout/", views.logout_view, name="logout"),
    path(
        "alterar-senha/", views.alterarsenha, name="alterar_senha"
    ),  
    path("perfil/", views.perfil, name="perfil"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
    path("recuperar-senha/", views.recuperarsenha, name="recuperar-senha"),
    path("vendedor/", views.vendedor, name="Vendedorperfil"),
    path('avaliacao/', views.avaliacao, name='lista_avaliacoes'),
    path('nova_avaliacao/', views.nova_avaliacao, name='nova_avaliacao'),


  # Rotas de Receitas
    path("receitas/", views.receitas, name="receitas"),
    path('receitas/<int:receita_id>/', views.receita_detalhe, name='receita_detalhe'),
    path("videos/", views.videos, name="videos"),
    path("receitas/criar/", views.cria_receita, name="cria_receita"),
  
    # Rotas de Produtos e Doação
    path('cadastro-produto/', views.cadastroproduto, name='cadastroproduto'), 
    path('doacao/', views.doacao, name='doacao'), 
    path('ong_pagina/<int:usuario_id>/', views.ongs_pagina, name='ongs_pagina'),

    # Rotas do Carrinho
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path("carrinho/adicionar/<int:produto_id>/",views.adicionar_carrinho,name="adicionar_carrinho",),

    path("checkout/", views.finalizar_pedido, name="finalizar_pedido"),
    path("remover_item/<int:item_id>/", views.remover_item, name="remover_item"),
    path("meus_pedidos/", views.meus_pedidos, name="meus_pedidos"),
    path("atualizar_carrinho/", views.atualizar_carrinho, name="atualizar_carrinho"),
    path("itemPedido/", views.ItemPedido, name="item_pedido"),
    
    # Rotas do Footer
    path("timedev/", views.devs, name="timedev"),
    path("dicas/", views.dicas, name="dicas"),
    path("cupom/", views.criar_cupom, name="cupom"),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
