from django.db import models

TIPO_NOTIFICACAO_CHOICES = (
    ('PEDIDO', 'Notificação de Pedido'),
    ('PROMOCAO', 'Promoção'),
    ('CUPOM', 'Cupom de Desconto'),
    ('NOVIDADE', 'Novidade do Sistema/App'),
)

class Notificacao(models.Model):
    # O usuário para quem a notificação se destina
    usuario = models.ForeignKey(
        'core.Perfil',
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Usuário'
    )
    
    # Campo para diferenciar o tipo de notificação
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_NOTIFICACAO_CHOICES,
        verbose_name='Tipo de Notificação'
    )
    
    titulo = models.CharField(max_length=255, verbose_name='Título')
    mensagem = models.TextField(verbose_name='Mensagem Completa')
    
    # URL ou ID que o usuário acessará ao clicar (ex: /pedidos/5, /cupom/novo)
    url_destino = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='URL de Destino'
    )
    
    lida = models.BooleanField(default=False, verbose_name='Lida')
    
    # Critério de Aceitação: Ordem Cronológica
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao'] 

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo} - {self.usuario.username}"