from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify

class CategoriaReceita(models.Model):
    """ Ex: 'Sobremesas', 'Pratos Principais', 'Saladas' """
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Receita(models.Model):
    """ Modelo principal para uma receita. """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    tempo_preparo = models.PositiveIntegerField(help_text="Tempo em minutos")
    rendimento = models.CharField(max_length=50, help_text="Ex: '8 porções' ou 'Serve 4 pessoas'")
    
    categoria = models.ForeignKey(CategoriaReceita, on_delete=models.SET_NULL, null=True, blank=True, related_name='receitas')
    
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
    quantidade = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantidade} de {self.nome}"

class EtapaPreparo(models.Model):
    """ Uma etapa do modo de preparo de uma receita. """
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='etapas')
    ordem = models.PositiveIntegerField(help_text="A ordem do passo (1, 2, 3...)")
    descricao = models.TextField()

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"Etapa {self.ordem}"

