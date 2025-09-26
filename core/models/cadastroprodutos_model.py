from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=225)
    descriacao = models.TextField()
    preco = models.DecimalField(maz_digits=8, decimal_places=2 )
    imagem = models.ImageField(upload_to='produtos/')
    destaques = models.BooleanField(default= False)

def __str__(self):
        return self.nome