from django.db import models
from .perfil_model import Perfil

class PerfilManager(models.Manager):
    """Manager customizado para o modelo Perfil"""
    
    def vendedores_ativos(self):
        """Retorna apenas vendedores ativos"""
        return self.filter(tipo=Perfil.TipoUsuario.VENDEDOR, usuario__is_active=True)
    
    def ongs_ativas(self):
        """Retorna apenas ONGs ativas"""
        return self.filter(tipo=Perfil.TipoUsuario.ONG, usuario__is_active=True)
    
    def clientes_ativos(self):
        """Retorna apenas clientes ativos"""
        return self.filter(tipo=Perfil.TipoUsuario.CLIENTE, usuario__is_active=True)