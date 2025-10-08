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

class CadastroForm(forms.ModelForm):
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
        fields = [ 
            "tipo",
            "nome_completo", # Adicionado para clientes
            "nome_negocio",
            "telefone", 
            "endereco",
            "cnpj",
            "descricao_parceiro",
        ]
        widgets = {
            "nome_completo": forms.TextInput(attrs={'placeholder':'Seu nome completo'}),
            "nome_negocio": forms.TextInput(attrs={'placeholder':'Nome da Loja/ONG'}),
            "telefone": forms.TextInput(attrs={'placeholder':'(11) 99999-9999'}),
            "cnpj": forms.TextInput(attrs={'placeholder':'CNPJ (se aplicável)'}),
            "descricao_parceiro": forms.Textarea(attrs={'placeholder':'Fale um pouco sobre você ou seu negócio...'}),
            "endereco": forms.TextInput(attrs={'placeholder':'Seu endereço completo'}),
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


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            "foto_perfil",
            "nome_completo",
            "nome_negocio",
            "telefone",
            "endereco",
            "cnpj",
            "descricao_parceiro",
        ]


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
        # Adicionando um label mais amigável para a categoria
        labels = {
            'categoria': 'Categoria da Receita'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrando o queryset para mostrar apenas categorias de receita
        self.fields["categoria"].queryset = CategoriaReceita.objects.all()

IngredienteFormSet = inlineformset_factory(
    Receita, Ingrediente, fields=("nome", "quantidade"), extra=1, can_delete=True
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
            "imagem_principal",
            "descricao",
            "codigo_produto",
            "data_validade",
        ]
        # REMOVIDO: O campo 'data_fabricacao' não existe no modelo Produto.
        # CORRIGIDO: O campo 'imagem' foi renomeado para 'imagem_principal' para corresponder ao modelo.
        
        widgets = {
            "data_validade": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CORRIGIDO: A referência a 'Categoria' foi alterada para 'CategoriaProduto'.
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
        # Garante que o código do cupom seja sempre salvo em maiúsculas
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
        # CORRIGIDO: Os campos foram alterados para 'nota' e 'texto' para corresponder ao modelo Avaliacao.
        fields = ['nota', 'texto']
        widgets = {
            'nota': forms.RadioSelect(choices=[(i, f'{i} Estrelas') for i in range(1, 6)]),
            'texto': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deixe seu comentário (opcional)...'}),
        }
        labels = {
            'nota': 'Sua Nota',
            'texto': 'Comentário'
        }

# REMOVIDO: O formulário 'ProdutovendedorForm' era redundante e se referia a um modelo inexistente.
# A funcionalidade dele deve ser coberta pelo 'ProdutoForm'.