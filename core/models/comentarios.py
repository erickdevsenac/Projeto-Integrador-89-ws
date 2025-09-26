from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg, Count
 
class Loja(models.Model):
    """
    Modelo simplificado para loja/vendedor
    """
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
   
    def __str__(self):
        return self.nome
   
    @property
    def total_comentarios(self):
        return self.comentarios.filter(aprovado=True).count()
   
    @property
    def media_avaliacoes(self):
        resultado = self.comentarios.filter(aprovado=True).aggregate(media=Avg('avaliacao'))
        return round(resultado['media'] or 0, 1)
 
 
class Comentario(models.Model):
    """
    Modelo para comentários/avaliações
    """
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
    curtidas = models.ManyToManyField(User, related_name='curtidas', blank=True)
   
    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_criacao']
   
    def __str__(self):
        return f"Comentário de {self.autor.username} - {self.avaliacao}★"
   
    def clean(self):
        """Validações básicas"""
        if self.autor == self.loja.proprietario:
            raise ValidationError("Você não pode comentar na sua própria loja")
   
    @property
    def total_curtidas(self):
        return self.curtidas.count()
   
    def usuario_curtiu(self, usuario):
        return self.curtidas.filter(id=usuario.id).exists()
   
    def toggle_curtida(self, usuario):
        """Adiciona ou remove curtida"""
        if self.usuario_curtiu(usuario):
            self.curtidas.remove(usuario)
            return False  # Curtida removida
        else:
            self.curtidas.add(usuario)
            return True  # Curtida adicionada
 
 
class ServicoComentarios:
    """
    Serviço para operações com comentários
    """
   
    @staticmethod
    def criar_comentario(loja_id, usuario_id, avaliacao, texto):
        """Cria um novo comentário"""
        from django.shortcuts import get_object_or_404
       
        loja = get_object_or_404(Loja, id=loja_id)
        usuario = get_object_or_404(User, id=usuario_id)
       
        # Verifica se usuário é o proprietário
        if usuario == loja.proprietario:
            raise ValidationError("Você não pode comentar na sua própria loja")
       
        # Cria o comentário
        comentario = Comentario(
            loja=loja,
            autor=usuario,
            avaliacao=avaliacao,
            texto=texto
        )
       
        comentario.full_clean()
        comentario.save()
        return comentario
   
    @staticmethod
    def curtir_comentario(comentario_id, usuario_id):
        """Curte ou descurte um comentário"""
        from django.shortcuts import get_object_or_404
       
        comentario = get_object_or_404(Comentario, id=comentario_id)
        usuario = get_object_or_404(User, id=usuario_id)
       
        return comentario.toggle_curtida(usuario)
   
    @staticmethod
    def listar_comentarios_loja(loja_id, ordenar_por='recentes'):
        """Lista comentários de uma loja"""
        comentarios = Comentario.objects.filter(loja_id=loja_id, aprovado=True)
       
        if ordenar_por == 'melhores':
            comentarios = comentarios.order_by('-avaliacao', '-data_criacao')
        elif ordenar_por == 'mais_curtidos':
            comentarios = comentarios.annotate(
                num_curtidas=Count('curtidas')
            ).order_by('-num_curtidas', '-data_criacao')
        else:  # recentes
            comentarios = comentarios.order_by('-data_criacao')
       
        return comentarios
   
    @staticmethod
    def estatisticas_loja(loja_id):
        """Estatísticas básicas da loja"""
        comentarios = Comentario.objects.filter(loja_id=loja_id, aprovado=True)
       
        total = comentarios.count()
        media = comentarios.aggregate(media=Avg('avaliacao'))['media'] or 0
       
        return {
            'total_comentarios': total,
            'media_avaliacoes': round(media, 1),
            'distribuicao': comentarios.values('avaliacao').annotate(
                total=Count('avaliacao')
            ).order_by('avaliacao')
        }
 
 
# Serializers para API
from rest_framework import serializers
 
class ComentarioSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source='autor.username', read_only=True)
    total_curtidas = serializers.IntegerField(read_only=True)
    usuario_curtiu = serializers.SerializerMethodField()
   
    class Meta:
        model = Comentario
        fields = [
            'id', 'autor', 'autor_nome', 'avaliacao', 'texto',
            'data_criacao', 'total_curtidas', 'usuario_curtiu'
        ]
        read_only_fields = ['id', 'autor', 'data_criacao']
   
    def get_usuario_curtiu(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.usuario_curtiu(request.user)
        return False
   
    def validate_avaliacao(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Avaliação deve ser entre 1 e 5")
        return value
   
    def validate_texto(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Comentário muito curto")
        if len(value) > 500:
            raise serializers.ValidationError("Comentário muito longo")
        return value
 
 
class CurtidaSerializer(serializers.Serializer):
    comentario_id = serializers.IntegerField()
    acao = serializers.ChoiceField(choices=['curtir', 'descurtir'])
 
 
class ComentarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = ['avaliacao', 'texto']
   
    def validate(self, data):
        # Validações adicionais podem ser adicionadas aqui
        return data
 
 
# Views simplificadas para API
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
 
class ComentarioViewSet(viewsets.ModelViewSet):
    """
    API para comentários - apenas criar, listar e curtir
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
   
    def get_queryset(self):
        return Comentario.objects.filter(aprovado=True)
   
    def get_serializer_class(self):
        if self.action == 'create':
            return ComentarioCreateSerializer
        return ComentarioSerializer
   
    def perform_create(self, serializer):
        loja_id = self.kwargs['loja_id']
        loja = Loja.objects.get(id=loja_id)
       
        # Verifica se usuário é o proprietário
        if self.request.user == loja.proprietario:
            return Response(
                {'error': 'Você não pode comentar na sua própria loja'},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        serializer.save(loja=loja, autor=self.request.user)
   
    @action(detail=True, methods=['post'])
    def curtir(self, request, pk=None):
        """Curte/descurte um comentário"""
        comentario = self.get_object()
        usuario = request.user
       
        try:
            curtida_adicionada = comentario.toggle_curtida(usuario)
            acao = 'curtido' if curtida_adicionada else 'descurtido'
           
            return Response({
                'acao': acao,
                'total_curtidas': comentario.total_curtidas,
                'usuario_curtiu': comentario.usuario_curtiu(usuario)
            })
           
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
 
 
# URLs básicas
from django.urls import path, include
from rest_framework.routers import DefaultRouter
 
router = DefaultRouter()
router.register(r'comentarios', ComentarioViewSet, basename='comentario')
 
urlpatterns = [
    path('api/lojas/<int:loja_id>/', include(router.urls)),
]
 
 
# Utilitários simples
class ComentarioUtils:
    """
    Utilitários para comentários
    """
   
    @staticmethod
    def formatar_estrelas(avaliacao):
        """Retorna string com estrelas"""
        return '★' * avaliacao + '☆' * (5 - avaliacao)
   
    @staticmethod
    def pode_comentar(usuario, loja):
        """Verifica se usuário pode comentar"""
        if usuario == loja.proprietario:
            return False, "Você não pode comentar na sua própria loja"
        return True, ""
   
    @staticmethod
    def comentarios_recentes(loja, limite=5):
        """Comentários mais recentes"""
        return Comentario.objects.filter(
            loja=loja,
            aprovado=True
        ).order_by('-data_criacao')[:limite]
 