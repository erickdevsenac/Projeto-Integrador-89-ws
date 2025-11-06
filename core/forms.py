from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import (
    Avaliacao,
    Cupom,
    EtapaPreparo,
    Ingrediente,
    Perfil,
    Produto,
    Receita,
    Pedido,
    CategoriaProduto,
    CategoriaReceita,
)


# ==============================================================================
# FORMULÁRIOS DE AUTENTICAÇÃO E PERFIL
# ==============================================================================

class CadastroStep1Form(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Digite seu email'}),
    )
    senha = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Crie uma senha forte'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirme sua senha'}),
    )
    
    class Meta:
        model = Perfil
        fields = ["tipo"]
        

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
            raise forms.ValidationError("A senha deve conter pelo menos um número.")
        return senha

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado!")
        return email


class CompleteClientProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["foto_perfil", "nome_completo", "telefone", "endereco", "cidade", "estado", "cep",]
        widgets = {
            "foto_perfil": forms.FileInput(),
            "nome_completo": forms.TextInput(attrs={'placeholder':'Seu nome completo'}),
            "telefone": forms.TextInput(attrs={'placeholder':'(11) 99999-9999', 'id': 'id_telefone'}),
            "cep": forms.TextInput(attrs={'id': 'id_cep'}),
            "endereco": forms.TextInput(attrs={'placeholder':'Rua, nº'}),
        }
        
class CompletePartnerProfileForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["foto_perfil", "nome_negocio", "cnpj", "descricao_parceiro", "telefone", "endereco"]
        widgets = {
            "foto_perfil": forms.FileInput(),
            "nome_negocio": forms.TextInput(attrs={'placeholder':'Nome da Loja/ONG'}),
            "cnpj": forms.TextInput(attrs={'placeholder':'CNPJ (se aplicável)', 'id': 'id_cnpj'}),
            "descricao_parceiro": forms.Textarea(attrs={'placeholder':'Fale um pouco sobre seu negócio...', "rows": 10,}),

            # "descricao_parceiro": forms.Textarea(attrs={'placeholder':'Fale um pouco sobre seu negócio...'}),
            "telefone": forms.TextInput(attrs={'placeholder':'(11) 99999-9999', 'id': 'id_telefone'}),
            "cep": forms.TextInput(attrs={'id': 'id_cep'}),
            "telefone": forms.TextInput(attrs={'placeholder':'(11) 99999-9999', 'id': 'id_telefone'}),
            "endereco": forms.TextInput(attrs={'placeholder':'Seu endereço completo'}),
        }


# ==============================================================================
# FORMULÁRIOS DE CONTEÚDO (RECEITAS, DICAS, ETC.)
# ==============================================================================

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = [
            "nome",
            "descricao",
            "tempo_preparo",
            "rendimento",
            "categoria",
            "imagem",
        ]
        labels = {
            'categoria': 'Categoria da Receita'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaReceita.objects.all()

IngredienteFormSet = inlineformset_factory(
    Receita,
    Ingrediente,
    fields=("nome", "quantidade"),
    extra=1,
    can_delete=True,
)

EtapaPreparoFormSet = inlineformset_factory(
    Receita, EtapaPreparo, fields=("ordem", "descricao"), extra=1, can_delete=True
)

# ==============================================================================
# FORMULÁRIOS DE E-COMMERCE (PRODUTO, CUPOM, CHECKOUT)
# ==============================================================================

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "nome",
            "categoria",
            "preco",
            "quantidade_estoque",
            "tipo_quantidade",
            "imagem_principal",
            "descricao",
            "codigo_produto",
            "data_validade",
        ]
        
        widgets = {
            "data_validade": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 10, "class": "richtext"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = CategoriaProduto.objects.all()
        self.fields["categoria"].label_from_instance = lambda obj: obj.nome

class CupomForm(forms.ModelForm):
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
        widgets = {
            "data_validade": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")
        return codigo.upper() if codigo else codigo

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['endereco_entrega', 'forma_pagamento']

        widgets = {
            'endereco_entrega': forms.Textarea(attrs={'rows': 3}),
            'forma_pagamento': forms.RadioSelect(),
        }
        labels = {
            'endereco_entrega': "Confirme ou altere o Endereço de Entrega",
            'forma_pagamento': "Escolha a Forma de Pagamento",
        }

# ==============================================================================
# OUTROS FORMULÁRIOS (AVALIAÇÃO, CONFIGURAÇÃO)
# ==============================================================================

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'texto']
        widgets = {
            'nota': forms.RadioSelect(choices=[(i, f'{i} Estrelas') for i in range(1, 6)]),
            'texto': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deixe seu comentário (opcional)...'}),
        }
        labels = {
            'nota': 'Sua Nota',
            'texto': 'Comentário'
        }
