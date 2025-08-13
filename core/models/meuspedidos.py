from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    
    def __str__(self):
        return self.nome

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aprovado'),
        ('C', 'Concluído'),
        ('R', 'Rejeitado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"
    
    def get_absolute_url(self):
        return reverse('detalhe_pedido', kwargs={'pk': self.pk})

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    def get_total_item(self):
        return self.quantidade * self.preco