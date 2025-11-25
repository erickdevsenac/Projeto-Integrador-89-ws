import pytest
from django.urls import reverse
 
def test_usuario_nao_logado_redirecionado_para_login(client):
    # Arrange
    url = reverse('core:ver_carrinho')
 
    # Act
    resposta = client.get(url)
 
    # Assert   
    assert resposta.status_code == 302
    assert "/login" in resposta.url
 
 
@pytest.mark.django_db
def test_usuario_logado_acessa_carrinho_com_sucesso(client, django_user_model):
    # Arrange
    usuario = django_user_model.objects.create_user(
        username='teste', password='123'
    )
    client.force_login(usuario)
   
    url = reverse('core:ver_carrinho')
 
    # Act
    resposta = client.get(url)
 
    # Assert
 
    assert resposta.status_code == 200