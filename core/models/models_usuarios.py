from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    class TipoUsuario(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        FORNECEDOR = 'FORNECEDOR', 'Fornecedor'
        ONG = 'ONG', 'ONG'

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tipo = models.CharField(max_length=20, choices=TipoUsuario.choices)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    endereco = models.TextField()
    cnpj = models.CharField("CNPJ", max_length=18, unique=True, null=True, blank=True, help_text="Obrigatório para Fornecedores e ONGs")
    descricao_parceiro = models.TextField("Descrição da Empresa/ONG", blank=True, help_text="Uma breve descrição sobre o parceiro")

    def __str__(self):
        return self.nome
    

# class Usuario(models.Model):
#     id_usuario = models.AutoField(primary_key=True)
#     nome = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     senha = models.CharField(max_length=128)
#     telefone = models.CharField(max_length=15)
#     endereco = models.TextField()

#     def __str__(self):
#         return self.nome


# class Cliente(Usuario):
#     restricao_alimenticia = models.CharField(max_length=255, blank=True, null=True)
#     realizar_pedido = models.CharField(max_length=255, blank=True, null=True)
#     solicitar_devolucao = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         verbose_name = 'Cliente'
#         verbose_name_plural = 'Clientes'


# class Fornecedor(Usuario):
#     cnpj = models.CharField(max_length=18, unique=True)
#     cadastrar_produtos = models.BooleanField(default=False)
#     editar_informacoes = models.BooleanField(default=False)
#     realizar_doacao = models.BooleanField(default=False)
#     cadastrar_estoque = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = 'Fornecedor'
#         verbose_name_plural = 'Fornecedores'


# class AdminSistema(Usuario):
#     permissao_geral = models.BooleanField(default=True)
#     observacoes = models.TextField(blank=True, null=True)

#     class Meta:
#         verbose_name = 'Administrador do Sistema'
#         verbose_name_plural = 'Administradores do Sistema'