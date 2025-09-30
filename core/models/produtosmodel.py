# from django.db import models

# class Produtos(models.Model):
#     nome = models.CharField(max_length=100)
#     descricao = models.TextField(blank= True)
#     preco = models.DecimalField(max_digits=10,decimal_places=2)
#     estoque = models.BooleanField(default=True)
#     criacao = models.DateTimeField(auto_now_add=True)
#     atualizado = models.DateTimeField(auto_now= True)

#     def __str__(self):
#         return self.nome