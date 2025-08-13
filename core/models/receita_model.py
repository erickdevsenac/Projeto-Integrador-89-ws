from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

class CategoriaReceita(models.Model):
    """ Ex: 'Sobremesas', 'Pratos Principais', 'Saladas' """
    nome = models.CharField(max_length=100, unique=True)
    # SUGESTÃO: slug é ótimo para URLs amigáveis (ex: /categorias/sobremesas)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.nome

class Receita(models.Model):
    """ Modelo principal para uma receita. """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tempo_preparo = models.PositiveIntegerField(help_text="Tempo em minutos")
    rendimento = models.CharField(max_length=50, help_text="Ex: '8 porções' ou 'Serve 4 pessoas'")
    
    categoria = models.ForeignKey(CategoriaReceita, on_delete=models.SET_NULL, null=True, blank=True, related_name='receitas')
    
    # MELHORIA: Adicionado autor e imagem
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='receitas_criadas'
    )
    imagem = models.ImageField(
        upload_to='receitas/',
        blank=True,
        null=True,
        help_text="Imagem de apresentação do prato"
    )
    
    data_criacao = models.DateTimeField(default=timezone.now)
    disponivel = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
    def __str__(self):
        return self.nome

class Ingrediente(models.Model):
    """ Um ingrediente específico para uma receita. """
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='ingredientes')
    nome = models.CharField(max_length=100)
    # Manter como CharField é simples e flexível (Ex: "1 xícara", "a gosto")
    quantidade = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantidade} de {self.nome}"

class EtapaPreparo(models.Model):
    """ Uma etapa do modo de preparo de uma receita. """
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='etapas')
    ordem = models.PositiveIntegerField(help_text="A ordem do passo (1, 2, 3...)")
    descricao = models.TextField()

    class Meta:
        ordering = ['ordem'] # Garante que as etapas sempre venham na ordem correta

    def __str__(self):
        return f"Etapa {self.ordem}"

class Avaliacao(models.Model):
    """ Modelo unificado para avaliações (nota) e comentários (texto). """
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='avaliacoes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    
    nota = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nota de 1 a 5 estrelas"
    )
    texto = models.TextField(
        "Comentário",
        blank=True,
        help_text="Escreva um comentário sobre a receita (opcional)"
    )
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('receita', 'autor') # Garante que um usuário só possa avaliar uma receita uma vez
        ordering = ['-data'] # Mostra as avaliações mais recentes primeiro

    def __str__(self):
        return f"Avaliação de {self.autor.username} para {self.receita.nome}"