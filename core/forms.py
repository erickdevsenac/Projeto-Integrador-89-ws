from turtle import width
from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import (
    Categoria,
    Cupom,
    EtapaPreparo,
    Ingrediente,
    Perfil,
    Produto,
    Receita,
    Pedido
)

class CadastroForm(forms.ModelForm):
    email = forms.EmailField(label="Email",  widget=forms.EmailInput(attrs={'placeholder': 'Digite seu email'}),)
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    confirmar_senha = forms.CharField(
        label="Confirmar Senha", widget=forms.PasswordInput(attrs={'placeholder': 'Senha'},)
    )
    
    class Meta:
        model = Perfil
        fields = [ 
            "tipo",
            "nome_negocio",
            "telefone", 
            "endereco",
            "cnpj",
            "descricao_parceiro",
            
        ]
        widgets = {
        "nome_negocio":forms.TextInput(attrs={'placeholder':'Nome do Negócio'}) ,
        "telefone":forms.TextInput(attrs={'placeholder':'Digite seu Telefone'}) ,
        "cnpj":forms.TextInput(attrs={'placeholder':'Digite seu CNPJ'}) ,
        "descricao_parceiro":forms.Textarea(attrs={'placeholder':'Descrição...'}) ,
        "endereco":forms.TextInput(attrs={'placeholder':'Seu Endereço'}) ,
    }

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
            raise forms.ValidationError(
                "A senha deve conter pelo menos uma letra maiúscula."
            )
        if not any(char.islower() for char in senha):
            raise forms.ValidationError(
                "A senha deve conter pelo menos uma letra minúscula."
            )
        if not any(char.isdigit() for char in senha):
            raise forms.ValidationError("A senha deve conter pelo menos um número")
        return senha

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado!")
        return email


class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        # Lista de campos do modelo Receita que o usuário irá preencher
        fields = [
            "nome",
            "descricao",
            "tempo_preparo",
            "rendimento",
            "categoria",
            "imagem",
        ]
        # Excluímos 'autor', 'data_criacao' e 'disponivel' porque serão
        # definidos automaticamente na view ou terão um valor padrão.


# --- Formsets para Itens Relacionados ---

# Cria um conjunto de formulários para os Ingredientes ligados a uma Receita
IngredienteFormSet = inlineformset_factory(
    Receita,  # Modelo Pai
    Ingrediente,  # Modelo Filho
    fields=("nome", "quantidade"),  # Campos do Ingrediente a serem exibidos
    extra=1,  # Quantos formulários em branco devem aparecer para adição
    can_delete=True,  # Permite que o usuário marque ingredientes para deletar
)

# Cria um conjunto de formulários para as Etapas de Preparo
EtapaPreparoFormSet = inlineformset_factory(
    Receita, EtapaPreparo, fields=("ordem", "descricao"), extra=1, can_delete=True
)


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            "nome_negocio",
            "telefone",
            "endereco",
            "foto_perfil",
            "descricao_parceiro",
            "cnpj",
        ]


class ConfiguracaoForm(forms.Form):
    # Opções de Tema
    tema_choices = [
        ("claro", "Claro"),
        ("escuro", "Escuro"),
    ]
    # Opções de Fonte
    fonte_choices = [
        ("normal", "Normal"),
        ("grande", "Grande"),
        ("extra_grande", "Extra Grande"),
    ]
    # Opções de Acessibilidade
    acessibilidade_choices = [
        ("nenhuma", "Nenhuma"),
        ("alto_contraste", "Alto Contraste"),
        ("leitura_facilitada", "Leitura Facilitada"),
    ]
    # Opções de Notificação
    notificacoes_choices = [
        ("sim", "Sim"),
        ("nao", "Não"),
    ]

    # Campos do formulário
    tema = forms.ChoiceField(choices=tema_choices, required=False)
    fonte = forms.ChoiceField(choices=fonte_choices, required=False)
    acessibilidade = forms.ChoiceField(choices=acessibilidade_choices, required=False)
    notificacoes = forms.ChoiceField(choices=notificacoes_choices, required=False)

    class Media:
        js = ("core/js/configuracao.js",)


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        # Lista de campos que o vendedor irá preencher
        fields = [
            "nome",
            "categoria",
            "preco",
            "quantidade_estoque",
            "imagem",
            "descricao",
            "codigo_produto",
            "data_fabricacao",
            "data_validade",
        ]
        # Excluímos 'vendedor', 'ativo' e 'data_criacao' porque serão
        # definidos automaticamente na view.

        # Adiciona widgets para melhorar a experiência do usuário
        widgets = {
            "data_fabricacao": forms.DateInput(attrs={"type": "date"}),
            "data_validade": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Deixa o campo de categoria mais amigável, mostrando os nomes
        self.fields["categoria"].queryset = Categoria.objects.all()
        self.fields["categoria"].label_from_instance = lambda obj: obj.nome


class CupomForm(forms.ModelForm):
    """
    Formulário para criar e editar objetos do modelo Cupom.
    """

    class Meta:
        model = Cupom
        fields = [
            "codigo",
            "tipo_desconto",
            "valor_desconto",
            "limite_uso",
            "data_validade",
            "valor_minimo_compra",
            "ativo",
        ]

        # Widgets ajudam a melhorar a aparência dos campos no HTML.
        widgets = {
            "data_validade": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")
        if codigo:
            return codigo.upper()
        return codigo

        
        

class CheckoutForm(forms.ModelForm):
    """
    Formulário para o cliente confirmar os detalhes do pedido.
    """
    class Meta:
        model = Pedido
        # Campos que o cliente irá preencher/confirmar
        fields = ['endereco_entrega', 'forma_pagamento']
        
        # Widgets para melhorar a aparência dos campos
        widgets = {
            'endereco_entrega': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'forma_pagamento': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Deixa os rótulos mais amigáveis
        self.fields['endereco_entrega'].label = "Endereço de Entrega"
        self.fields['forma_pagamento'].label = "Escolha a Forma de Pagamento"
