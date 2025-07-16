from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('produtos/', views.produtos, name='produtos'),
    path('contato/', views.contato, name='contato'),
    path('telalogin/', views.telalogin, name='telalogin'),
    path('trocasenha/', views.trocasenha, name='troca-senha'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('receitas/', views.receitas, name= 'receitas')
]