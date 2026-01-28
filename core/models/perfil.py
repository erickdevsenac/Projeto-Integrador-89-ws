from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .time_stamp import TimeStampedModel


class PerfilManager(models.Manager):
    """Manager customizado para o modelo Perfil"""

    def vendedores_ativos(self):
        """Retorna apenas perfis de Vendedores ativos"""
        return self.filter(
            tipo=self.model.TipoUsuario.VENDEDOR, ativo=True, usuario__is_active=False
        )

    def ongs_ativas(self):
        """Retorna apenas perfis de ONGs ativas"""
        return self.filter(
            tipo=self.model.TipoUsuario.ONG, ativo=True, usuario__is_active=False
        )

    def clientes_ativos(self):
        """Retorna apenas perfis de Clientes ativos"""
        return self.filter(
            tipo=self.model.TipoUsuario.CLIENTE, ativo=True, usuario__is_active=False
        )


class Perfil(TimeStampedModel):
    """
    Modelo para perfis de usuário, servindo como Cliente, Vendedor (Loja) ou ONG.
    """

    class TipoUsuario(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        VENDEDOR = "VENDEDOR", "Vendedor"
        ONG = "ONG", "ONG"

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tipo = models.CharField(max_length=10, choices=TipoUsuario.choices)
    avaliacoes = GenericRelation("Avaliacao")

    # --- CAMPOS COMUNS A TODOS OS USUÁRIOS ---
    foto_perfil = models.ImageField(
        upload_to="fotos_perfil/",
        blank=True,
        null=True,
        help_text="Foto do perfil ou logo da empresa/ONG.",
    )
    telefone = models.CharField(
        max_length=20, blank=True, help_text="Telefone com DDD, ex: (11) 99999-9999"
    )
    endereco = models.CharField(max_length=255)
    cep = models.CharField(
        max_length=10, help_text="CEP no formato 00000-000"
    )
    cidade = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=2, help_text="Sigla do estado, ex: SP"
    )

    # --- CAMPO ESPECÍFICO PARA CLIENTES ---
    nome_completo = models.CharField(
        "Nome Completo",
        max_length=255,
        help_text="Nome completo do cliente.",
    )

    # --- CAMPOS ESPECÍFICOS PARA VENDEDORES E ONGS ---
    nome_negocio = models.CharField(
        "Nome da Loja/ONG",
        max_length=255,
        help_text="O nome comercial do vendedor ou da ONG.",
    )
    cnpj = models.CharField(
        "CNPJ",
        max_length=18,
        unique= True,
        help_text="Obrigatório para Vendedores e ONGs.",
    )
    descricao_parceiro = models.TextField(
        "Descrição da Empresa/ONG",
        help_text="Uma breve descrição sobre o parceiro.",
    )

    # --- CAMPOS ESPECÍFICOS APENAS PARA ONGS ---
    imagem_carrossel1 = models.ImageField(upload_to="carrossel/")
    imagem_carrossel2 = models.ImageField(upload_to="carrossel/")
    imagem_carrossel3 = models.ImageField(upload_to="carrossel/")
    objetivo = models.TextField("Objetivos da ONG")

    # --- AVALIAÇÕES (APENAS PARA VENDEDORES) ---
    avaliacao_media = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Avaliação média do vendedor (0-5).",
    )
    total_avaliacoes = models.PositiveIntegerField(default=0)

    verificado = models.BooleanField(
        default=False, help_text="Perfil verificado pela administração."
    )
    ativo = models.BooleanField(default=True, help_text="Perfil ativo no sistema.")

    objects = PerfilManager()

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        indexes = [
            models.Index(fields=["tipo", "ativo"]),
            models.Index(fields=["cidade", "estado"]),
        ]

    def __str__(self):
        if (
            self.tipo in [self.TipoUsuario.VENDEDOR, self.TipoUsuario.ONG]
            and self.nome_negocio
        ):
            return self.nome_negocio
        if self.tipo == self.TipoUsuario.CLIENTE and self.nome_completo:
            return self.nome_completo
        # Fallback para o nome de usuário do Django User
        return self.usuario.get_full_name() or self.usuario.username

    def get_absolute_url(self):
        if self.tipo == self.TipoUsuario.ONG:
            return reverse("core:ongs_pagina", kwargs={"usuario_id": self.usuario.id})
        return reverse("core:perfil")

    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado."""
        parts = [self.endereco, self.cidade, self.estado, self.cep]
        return ", ".join(p for p in parts if p)
