from django import forms
from .models import Review

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comentario', 'avaliacao']
        widgets = {
            'comentario': forms.Textarea(attrs={'placeholder': 'Escreva sua review...'}),
            # avaliação opcional, com 1 a 5 estrelas
            'avaliacao': forms.RadioSelect(choices=[(i, f'{i} Estrelas') for i in range(1, 6)])  # exibe as estrelas como opções
        }

    # deixa o campo de avaliação opcional (não obrigatório)
    avaliacao = forms.IntegerField(
        required=False,  # o campo de avaliação não é obrigatório
        widget=forms.RadioSelect(choices=[(i, f'{i} Estrelas') for i in range(1, 6)]) 
    )

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')