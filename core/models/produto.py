import uuid
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from .time_stamp import TimeStampedModel


class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Versão do nome amigável para URLs, ex: 'dicas-sustentaveis'",
    )

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ProdutoManager(models.Manager):
    """Manager customizado para o modelo Produto"""

    def disponiveis(self):
        return self.filter(ativo=True, quantidade_estoque__gt=0)

    def por_categoria(self, categoria_slug):
        return self.disponiveis().filter(categoria__slug=categoria_slug)

    def buscar(self, termo):
        return self.disponiveis().filter(
            Q(nome__icontains=termo)
            | Q(descricao__icontains=termo)
            | Q(categoria__nome__icontains=termo)
        )


class Produto(TimeStampedModel):
    avaliacoes = GenericRelation("Avaliacao")

    class MotivoDesconto(models.TextChoices):
        VALIDADE_PROXIMA = "VALIDADE", "Próximo da Validade"
        DEFEITO_ESTETICO = "ESTETICA", "Defeito Estético"
        EXCESSO_ESTOQUE = "EXCESSO", "Excesso de Estoque"

    class TipoPesagem(models.TextChoices):
        QUILO = "PESA", "Kg"
        LITRO = "MEDE", "Litros"
        UNIDADE = "QUANTIA", "Unidade"

    vendedor = models.ForeignKey(
        "core.Perfil",
        on_delete=models.CASCADE,
        related_name="produtos",
        limit_choices_to={"tipo": "VENDEDOR"},
    )

    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produtos",
    )

    preco = models.DecimalField(
        "Preço de Venda",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    preco_original = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preço original do produto, antes do desconto.",
    )

    motivo_desconto = models.CharField(
        max_length=10,
        choices=MotivoDesconto.choices,
        blank=True,
        null=True,
        help_text="Motivo do desconto.",
    )

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    imagem_principal = models.ImageField(upload_to="produtos/", blank=True, null=True)

    quantidade_estoque = models.PositiveIntegerField(default=0)

    estoque_minimo = models.PositiveIntegerField(
        default=1,
        help_text="Quantidade mínima para alerta de estoque baixo",
    )

    tipo_quantidade = models.CharField(
        choices=TipoPesagem.choices,
        max_length=50,
    )

    codigo_produto = models.CharField(
        "Código (SKU)",
        max_length=50,
        unique=True,
        blank=True,
        help_text="Será gerado automaticamente se deixado em branco.",
    )

    data_validade = models.DateField(
        "Data de Validade",
        blank=True,
        null=True,
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Desmarque para pausar o anúncio do produto.",
    )

    destaque = models.BooleanField(default=False)

    visualizacoes = models.PositiveIntegerField(default=0, editable=False)

    objects = ProdutoManager()

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["-data_criacao"]
        indexes = [
            models.Index(fields=["ativo", "quantidade_estoque"]),
            models.Index(fields=["categoria", "ativo"]),
            models.Index(fields=["vendedor", "ativo"]),
        ]

    def __str__(self):
        return f"{self.nome} | {self.vendedor.nome_negocio or self.vendedor.usuario.username}"

    def get_absolute_url(self):
        return reverse("core:produto_detalhe", kwargs={"produto_id": self.pk})

    def save(self, *args, **kwargs):
        if not self.codigo_produto:
            self.codigo_produto = f"PROD-{uuid.uuid4().hex[:8].upper()}"

        if self.nome:
            self.nome = self.nome.capitalize()

        super().save(*args, **kwargs)

    # ---------------- PROPERTIES ---------------- #

    @property
    def imagem(self):
        return self.imagem_principal

    @property
    def verifica_vendedor(self):
        return self.vendedor.tipo == "VENDEDOR"

    @property
    def disponivel_para_venda(self):
        return self.ativo and self.quantidade_estoque > 0

    @property
    def estoque_baixo(self):
        return (
            self.quantidade_estoque > 0
            and self.quantidade_estoque <= self.estoque_minimo
        )


class PacoteSurpresa(TimeStampedModel):

    tipo_conteudo = models.CharField(
        max_length=100,
        blank=True,
    )

    instrucoes_especiais = models.TextField(blank=True)

    data_disponibilidade_inicio = models.DateField(blank=True, null=True)
    data_disponibilidade_fim = models.DateField(blank=True, null=True)

    produtos_possiveis = models.ManyToManyField(
        "Produto",
        blank=True,
    )

    vendedor = models.ForeignKey(
        "core.Perfil",
        on_delete=models.CASCADE,
        related_name="pacotes",
        limit_choices_to={"tipo": "VENDEDOR"},
    )

    nome = models.CharField(max_length=100, default="Pacote Surpresa do Dia")
    descricao = models.TextField()
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    imagem = models.ImageField(upload_to="pacotes/", blank=True, null=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pacote Surpresa"
        verbose_name_plural = "Pacotes Surpresa"

    def __str__(self):
        return f"{self.nome} - {self.vendedor.nome_negocio}"

    @property
    def esta_disponivel_agora(self):
        from django.utils import timezone

        now = timezone.now().date()

        if not self.ativo or self.quantidade_estoque <= 0:
            return False

        if self.data_disponibilidade_inicio and now < self.data_disponibilidade_inicio:
            return False

        if self.data_disponibilidade_fim and now > self.data_disponibilidade_fim:
            return False

        return True