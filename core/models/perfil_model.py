from django.db import models
from django.contrib.auth.models import User
from .time_stamp_model import TimeStampedModel
from .perfil_manager import PerfilManager

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Perfil(TimeStampedModel):
    """Modelo melhorado para perfis de usuário"""
    
    class TipoUsuario(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        VENDEDOR = 'VENDEDOR', 'Vendedor'
        ONG = 'ONG', 'ONG'

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tipo = models.CharField(max_length=20, choices=TipoUsuario.choices)
    
    # Informações básicas
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/', 
        blank=True, 
        null=True,
        help_text="Foto do perfil do usuário"
    )
    telefone = models.CharField(
        max_length=20, 
        help_text="Telefone com DDD, ex: (11) 99999-9999"
    )
    endereco = models.CharField(max_length=255)
    cep = models.CharField(
        max_length=10, 
        blank=True, 
        help_text="CEP no formato 00000-000"
    )
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True, help_text="Sigla do estado, ex: SP")
    
    # Campos específicos para vendedores e ONGs
    nome_negocio = models.CharField(
        "Nome da Loja/Negócio",
        max_length=255,
        blank=True,
        help_text="O nome comercial do vendedor ou da ONG."
    )
    cnpj = models.CharField(
        "CNPJ", 
        max_length=18, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="Obrigatório para Vendedores e ONGs"
    )
    descricao_parceiro = models.TextField(
        "Descrição da Empresa/ONG", 
        blank=True, 
        help_text="Uma breve descrição sobre o parceiro"
    )
    
    # Campos específicos para ONGs
    logo_ong = models.ImageField(
        upload_to='logos_ong/', 
        blank=True, 
        null=True,
        help_text="Logo da ONG"
    )
    imagem_carrossel1 = models.ImageField(
        upload_to='carrossel/', 
        blank=True, 
        null=True, 
        help_text="Primeira imagem do carrossel (apenas para ONGs)"
    )
    imagem_carrossel2 = models.ImageField(
        upload_to='carrossel/', 
        blank=True, 
        null=True, 
        help_text="Segunda imagem do carrossel (apenas para ONGs)"
    )
    imagem_carrossel3 = models.ImageField(
        upload_to='carrossel/', 
        blank=True, 
        null=True, 
        help_text="Terceira imagem do carrossel (apenas para ONGs)"
    )
    objetivo = models.TextField(
        "Objetivos da ONG", 
        blank=True, 
        help_text="Descrição dos objetivos e trabalhos da ONG"
    )
    
    # Campos de controle
    verificado = models.BooleanField(
        default=False, 
        help_text="Perfil verificado pela administração"
    )
    ativo = models.BooleanField(
        default=True, 
        help_text="Perfil ativo no sistema"
    )
    
    # Avaliações (para vendedores)
    avaliacao_media = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Avaliação média do vendedor (0-5)"
    )
    total_avaliacoes = models.PositiveIntegerField(
        default=0,
        help_text="Total de avaliações recebidas"
    )

    objects = PerfilManager()

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        indexes = [
            models.Index(fields=['tipo', 'ativo']),
            models.Index(fields=['cidade', 'estado']),
        ]

    def __str__(self):
        if self.tipo == self.TipoUsuario.VENDEDOR and self.nome_negocio:
            return self.nome_negocio
        return self.usuario.get_full_name() or self.usuario.username
    
    def get_absolute_url(self):
        if self.tipo == self.TipoUsuario.ONG:
            return reverse('core:ongs_pagina', kwargs={'usuario_id': self.usuario.id})
        return reverse('core:perfil')
    
    @property
    def nome_completo(self):
        """Retorna o nome completo do usuário"""
        return self.usuario.get_full_name() or self.usuario.username
    
    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado"""
        endereco_parts = [self.endereco]
        if self.cidade:
            endereco_parts.append(self.cidade)
        if self.estado:
            endereco_parts.append(self.estado)
        if self.cep:
            endereco_parts.append(self.cep)
        return ', '.join(endereco_parts)