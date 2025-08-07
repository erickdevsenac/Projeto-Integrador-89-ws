from django.db import models

class Doacao(models.Model):
    """
    Registra uma doação de produtos para uma ONG parceira.
    """
    class StatusDoacao(models.TextChoices):
        AGUARDANDO_RETIRADA = 'AGUARDANDO', 'Aguardando Retirada'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada'

    ong = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.PROTECT, 
        limit_choices_to={'tipo': 'ONG'},
        related_name='doacoes_recebidas' # Ajuda a diferenciar as relações no modelo Perfil
    )

    doador = models.ForeignKey(
        'core.Perfil', 
        on_delete=models.PROTECT, 
        limit_choices_to={'tipo': 'FORNECEDOR'}, 
        help_text="Fornecedor que está doando",
        related_name='doacoes_feitas'
    )
    
    descricao = models.TextField(help_text="Descrição dos itens doados")
    quantidade_doada = models.PositiveIntegerField()

    data_doacao = models.DateTimeField() 
    
    status = models.CharField(max_length=20, choices=StatusDoacao.choices, default=StatusDoacao.AGUARDANDO_RETIRADA)
    
    def __str__(self):
        return f"Doação de {self.doador} para {self.ong}"