from django.db import models
from django.contrib.auth.models import User

class Avaliacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)
    nota = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Estrela{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação {self.nota} estrela{'s' if self.nota > 1 else ''} por {self.usuario or 'anônimo'}"