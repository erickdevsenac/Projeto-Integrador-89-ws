# Em core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Rotas Principais
    path('', views.index, name='index'),
    path('produtos/', views.produtos, name='produtos'),
    path('busca/', views.buscarprodutos, name='buscar_produtos'),
    path('contato/', views.contato, name='contato'),

    # Rotas de Autenticação e Usuário
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='telalogin'), # BOA PRÁTICA: URL mais curta
    path('logout/', views.logout_view, name='logout'),
    path('alterar-senha/', views.alterarsenha, name='alterar_senha'), # BOA PRÁTICA: URL com hífen

    # Rotas de Receitas
    path('receitas/', views.receitas, name='receitas'),
    path('videos/', views.videos, name='videos'),
    # Lembre-se de adicionar a URL para criar receitas também
    # path('receitas/criar/', views.cria_receita, name='cria_receita'),

    # Rotas de Produtos e Doação
    path('cadastro-produto/', views.cadastroproduto, name='cadastroproduto'), # BOA PRÁTICA: URL com hífen
    path('doacao/', views.doacao, name='doacao'), 

    # Rotas do Carrinho
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'), 
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
]