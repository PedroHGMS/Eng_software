# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Um formulário de criação de usuário customizado para adicionar a classe CSS.
    O UserCreationForm padrão já inclui username, password e password confirmation.
    Se você precisar de email, pode adicioná-lo aqui, mas o padrão auth.User
    só exige username e password. Podemos querer adicionar email para que
    o usuário possa logar com email ou username.
    """
    email = forms.EmailField(required=True, label="Email") # Adiciona campo de email

    class Meta(UserCreationForm.Meta):
        model = User
        # Use fields para especificar a ordem ou adicionar campos extras
        fields = UserCreationForm.Meta.fields + ('email',) # Adiciona 'email' aos campos padrão

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classe CSS a todos os campos
        for field_name, field in self.fields.items():
             field.widget.attrs.update({'class': 'form-control'})
             # Adiciona placeholders (opcional)
             if field_name == 'username':
                 field.widget.attrs.update({'placeholder': 'Nome de usuário'})
             elif field_name == 'email':
                 field.widget.attrs.update({'placeholder': 'seu@email.com'})
             elif field_name == 'password1':
                  field.label = "Senha" # Mudar label padrão 'Password'
                  field.widget.attrs.update({'placeholder': '********'})
             elif field_name == 'password2':
                  field.label = "Confirme a Senha" # Mudar label padrão 'Password confirmation'
                  field.widget.attrs.update({'placeholder': '********'})


# Opcional: Adicionar classe CSS ao formulário de login existente
class CustomAuthenticationForm(AuthenticationForm):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            # Adiciona placeholders (opcional)
            if field_name == 'username':
                 field.widget.attrs.update({'placeholder': 'Nome de usuário ou Email'}) # Ajustar placeholder
            elif field_name == 'password':
                 field.widget.attrs.update({'placeholder': '********'})