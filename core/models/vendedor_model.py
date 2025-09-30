from django.db import models
from django.contrib.auth.models import User
from core.models.produto_model import Categoria

class ProdutoVendedor(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_produto = models.CharField(max_length=20, unique=True)
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)

    descricao = models.TextField(null=True, blank=True)  # Você manteve esse
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos_de_vendedores')


    def __str__(self):
        return self.nome

class EstatisticaVenda(models.Model):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE, related_name="estatisticas")
    total_vendas = models.PositiveIntegerField(default=0)
    receita_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Estatísticas de {self.loja.nome}"
