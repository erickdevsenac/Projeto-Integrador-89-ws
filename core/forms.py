from django import forms
from django.forms import inlineformset_factory
from .models import Perfil, Receita, Ingrediente, EtapaPreparo
from django.contrib.auth.models import User

class CadastroForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(label="Confirmar Senha", widget=forms.PasswordInput)

    class Meta:
        model = Perfil
        fields = ['tipo', 'nome_negocio', 'telefone', 'endereco', 'cnpj', 'descricao_parceiro']

    def clean_confirmar_senha(self):
        senha = self.cleaned_data.get("senha")
        confirmar_senha = self.cleaned_data.get("confirmar_senha")
        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não conferem!")
        return confirmar_senha
    
    def clean_senha(self):
        senha = self.cleaned_data.get("senha")
        if len(senha) < 6:
            raise forms.ValidationError("A senha deve ter pelo menos 6 caracteres.")
        if not any(char.isupper() for char in senha):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not any(char.islower() for char in senha):
            raise forms.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not any(char.isdigit() for char in senha):
            raise forms.ValidationError("A senha deve conter pelo menos um número")
        return senha

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado!")
        return email
    
class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        # Lista de campos do modelo Receita que o usuário irá preencher
        fields = [
            'nome', 
            'descricao', 
            'tempo_preparo', 
            'rendimento', 
            'categoria', 
            'imagem'
        ]
        # Excluímos 'autor', 'data_criacao' e 'disponivel' porque serão
        # definidos automaticamente na view ou terão um valor padrão.

# --- Formsets para Itens Relacionados ---

# Cria um conjunto de formulários para os Ingredientes ligados a uma Receita
IngredienteFormSet = inlineformset_factory(
    Receita,          # Modelo Pai
    Ingrediente,      # Modelo Filho
    fields=('nome', 'quantidade'), # Campos do Ingrediente a serem exibidos
    extra=1,          # Quantos formulários em branco devem aparecer para adição
    can_delete=True   # Permite que o usuário marque ingredientes para deletar
)

# Cria um conjunto de formulários para as Etapas de Preparo
EtapaPreparoFormSet = inlineformset_factory(
    Receita,
    EtapaPreparo,
    fields=('ordem', 'descricao'),
    extra=1,
    can_delete=True
)

#Lista de Pedidos
from django import forms
from .models import Pedido, ItemPedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = []
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def save(self, commit=True):
        pedido = super().save(commit=False)
        if commit:
            pedido.save()
        return pedido