from django.db import models

class Produto(models.Model):
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pendente', 'Pendente'),
        ('em_preparo', 'Em Preparo'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado')
    ], default='pendente')

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.nome}'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome}'


class Compra(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='compras')
    fornecedor = models.ForeignKey('Fornecedor', on_delete=models.CASCADE)
    data_compra = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'Compra #{self.id} - Pedido #{self.pedido.id} - Fornecedor: {self.fornecedor.nome}'
