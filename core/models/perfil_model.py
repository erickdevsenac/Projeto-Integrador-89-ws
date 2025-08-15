from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    class TipoUsuario(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        VENDEDOR = 'VENDEDOR', 'Vendedor'
        ONG = 'ONG', 'ONG'

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tipo = models.CharField(max_length=20, choices=TipoUsuario.choices)

    nome_negocio = models.CharField(
        "Nome da Loja/Negócio",
        max_length=255,
        blank=True,
        help_text="O nome comercial do vendedor ou da ONG."
    )
    
    logo_ong = models.ImageField(null=True)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    cnpj = models.CharField("CNPJ", max_length=18, unique=True, null=True, blank=True, help_text="Obrigatório para Vendedores e ONGs")
    descricao_parceiro = models.TextField("Descrição da Empresa/ONG", blank=True, help_text="Uma breve descrição sobre o parceiro")
    imagem_carrossel1 = models.ImageField(upload_to='carrossel/', null=True, blank=True, help_text="Apenas para ONGs")
    imagem_carrossel2 = models.ImageField(upload_to='carrossel/', null=True, blank=True, help_text="Apenas para ONGs")
    imagem_carrossel3 = models.ImageField(upload_to='carrossel/', null=True, blank=True, help_text="Apenas para ONGs")
    objetivo = models.TextField("Descrição da Empresa/ONG", null=True, blank=True, help_text="Descrição dos seus objetivos e trabalhos da ONG")

    def __str__(self):
        if self.tipo == self.TipoUsuario.VENDEDOR and self.nome_negocio:
            return self.nome_negocio
            
        return self.usuario.get_full_name() or self.usuario.username
    