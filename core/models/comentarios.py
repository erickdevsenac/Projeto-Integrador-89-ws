from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .loja import Loja

class Comentario(models.Model):
    AVALIACAO_CHOICES = [
        (1, '1 Estrela'),
        (2, '2 Estrelas'),
        (3, '3 Estrelas'),
        (4, '4 Estrelas'),
        (5, '5 Estrelas'),
    ]

    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    avaliacao = models.IntegerField(choices=AVALIACAO_CHOICES)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(default=True)  # Auto-aprovado para simplificar
    curtidas = models.ManyToManyField(User, related_name='curtidas_comentarios', blank=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Comentário de {self.autor.username} - {self.avaliacao}★"

    def clean(self):
        if self.autor == self.loja.proprietario:
            raise ValidationError("Você não pode comentar na sua própria loja")

    @property
    def total_curtidas(self):
        return self.curtidas.count()

    def usuario_curtiu(self, usuario):
        return self.curtidas.filter(id=usuario.id).exists()

    def toggle_curtida(self, usuario):
        if self.usuario_curtiu(usuario):
            self.curtidas.remove(usuario)
            return False 
        else:
            self.curtidas.add(usuario)
            return True  