from django.contrib.auth.models import User
from core.models.perfil import Perfil
import pytest

@pytest.fixture
def vendedor_fake():
    user = User.objects.create_user(
        username="vendedor_global", 
        password="123"
        )
    
    perfil = Perfil.objects.create(
        usuario = user,
        tipo = Perfil.TipoUsuario.VENDEDOR,
        nome_negocio = "Loja Global do Pytest"
    )
    return perfil

@pytest.fixture
def cliente_fake():
    user = User.objects.create_user(
        username="cliente_global", 
        password="123"
        )
    
    perfil = Perfil.objects.create(
        usuario = user,
        tipo = Perfil.TipoUsuario.CLIENTE,
    )
    return perfil
