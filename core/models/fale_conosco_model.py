from django.db import models


class FaleConosco(models.Model):
    class statusMensagem(models.TextChoices):
        NOVA = "NOVA", "Nova"
        RESPONDIDA = "RESPONDIDA", "Respondida"
        FECHADA = "FECHADA", "Fechada"

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    mensagem = models.TextField(help_text="conteudo da mensagem")
    data_envio = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=statusMensagem.choices, default=statusMensagem.NOVA
    )

    def __str__(self):
        return f"Mensagem de {self.nome} - {self.assunto}"
