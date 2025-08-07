from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('produtos/', views.produtos, name='produtos'),
    path('contato/', views.contato, name='contato'),
    path('telalogin/', views.telalogin, name='telalogin'),
    path('trocasenha/', views.trocasenha, name='troca-senha'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('videos/',views.videos,name='videos'),
    path('receitas/', views.receitas, name= 'receitas'),
    path('busca/', views.buscar_produtos, name= 'buscar_produtos'),
    path('cadastroproduto/', views.cadastroproduto, name='cadastroproduto')
]