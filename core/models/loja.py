from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Loja(models.Model):
    """
    Modelo simplificado para loja/vendedor
    """
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    imagem = models.ImageField(upload_to="lojas/", null=True, blank=True)
    localizacao = models.CharField(max_length=255)
   
    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
   
    def __str__(self):
        return self.nome
   
    @property
    def total_comentarios(self):
        return self.comentarios.filter(aprovado=True).count()
   
    @property
    def media_avaliacoes(self):
        resultado = self.comentarios.filter(aprovado=True).aggregate(media=Avg('avaliacao'))
        return round(resultado['media'] or 0, 1)