from django.db import models
from django.contrib.auth.models import User

class Receita(models.Model):
    pessoa = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    ingredientes = models.TextField()
    modo_preparo = models.TextField()
    imagem = models.ImageField(upload_to='receitas/', null=True, blank=True)
   