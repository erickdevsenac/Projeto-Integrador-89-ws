from django.db import models
from django.conf import settings
from django.utils import timezone

class CategoriaDica(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria de Dica"
        verbose_name_plural = "Categorias de Dicas"

    def __str__(self):
        return self.nome

class Dica(models.Model):
    titulo = models.CharField(max_length=200)
    resumo = models.CharField(max_length=255, help_text="Um resumo curto que aparecerá no card da dica.")
    conteudo = models.TextField(help_text="O conteúdo completo da dica.")
    
    imagem = models.ImageField(upload_to='dicas/', blank=True, null=True)
    
    categoria = models.ForeignKey(
        CategoriaDica, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dicas'
    )
    
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="O autor da dica."
    )
    
    publicada = models.BooleanField(default=True)
    data_publicacao = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data_publicacao'] 

    def __str__(self):
        return self.titulo