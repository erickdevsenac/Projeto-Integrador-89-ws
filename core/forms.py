from django import forms
from .models import Perfil
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