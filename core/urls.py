from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('produtos/', views.produtos, name='produtos'),
    path('contato/', views.contato, name='contato'),
    path('telalogin/', views.login, name='telalogin'),
    path('alterarsenha/', views.alterarsenha, name='alterar_senha'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('videos/',views.videos,name='videos'),
    path('receitas/', views.receitas, name= 'receitas'),
    path('busca/', views.buscarprodutos, name= 'buscar_produtos'),
    path('cadastroproduto/', views.cadastroproduto, name='cadastroproduto'),
    path('doacao/', views.doacao, name='docao'),
    path('logout/', views.logout_view, name='logout'),
]