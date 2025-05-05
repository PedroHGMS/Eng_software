# users/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse # Importar reverse
from django.contrib.auth.decorators import login_required

# Importar seus formulários (manter a importação, mesmo que não usemos o AuthenticationForm na view POST)
from .forms import CustomUserCreationForm, CustomAuthenticationForm # Assumindo que CustomAuthenticationForm está definido


User = get_user_model() # Obtém o modelo de usuário ativo


# Modificar a view de login para usar email
def login_view(request):
    # Se a requisição for POST (tentativa de login)
    if request.method == 'POST':
        # Obter email e senha dos dados POST do formulário
        # Note que seus inputs HTML têm name="email" e name="senha"
        identificador = request.POST.get('email') # Recebe o que foi digitado no campo 'email'
        senha = request.POST.get('senha')       # Recebe o que foi digitado no campo 'senha'

        # Tentar encontrar o usuário pelo EMAIL fornecido
        user = None # Inicializa user como None
        try:
            # Usa filter().first() ao invés de get() para evitar exceção DoesNotExist
            # Se múltiplos usuários tiverem o mesmo email (não deveria acontecer com unique=True), pega o primeiro
            user_obj = User.objects.filter(email__iexact=identificador).first() # Usa __iexact para busca case-insensitive no email

            # Se o usuário foi encontrado pelo email
            if user_obj:
                # Verificar a senha usando o método check_password() do objeto User
                # Este é o método correto para verificar senhas hashed
                if user_obj.check_password(senha):
                    user = user_obj # Senha correta, usuário autenticado

        except Exception as e:
            # Logar qualquer erro inesperado durante a busca ou verificação
            print(f"Erro durante o processo de login: {e}")
            # O erro de login abaixo já cobrirá a falha

        # Se user não for None neste ponto, significa que o email foi encontrado E a senha está correta
        if user is not None:
            # Logar o usuário na sessão
            login(request, user)
            # Opcional: Adicionar uma mensagem de sucesso (será exibida na próxima página)
            messages.success(request, f'Bem-vindo(a), {user.username}!') # Ou user.email se preferir

            # Redirecionar para a URL 'next' se ela existir (ex: ?next=/reviews/make/),
            # caso contrário, redirecionar para a página 'reviews:all_reviews'
            # Use reverse() para gerar a URL nomeada de forma segura
            redirect_url = request.GET.get('next', reverse('reviews:all_reviews'))
            return redirect(redirect_url)

        else:
            # Se o usuário não foi encontrado pelo email OU a senha estava incorreta
            # Adicionar uma mensagem de erro
            messages.error(request, 'Email ou senha inválidos.')
            # Redirecionar de volta para a página de login (geralmente é uma requisição GET)
            # Isso faz com que a mensagem de erro seja exibida na página de login
            # Use reverse() para gerar a URL nomeada de forma segura
            return redirect(reverse('users:login')) # Redireciona para a URL de login do app 'users'


    # Se a requisição for GET (apenas exibir o formulário de login)
    else:
        # Nada específico precisa ser feito aqui além de renderizar o template.
        # Se você não está usando um form object para renderizar os campos no template HTML,
        # não precisa criar uma instância do formulário aqui.
        pass # A view apenas continua para a linha de renderização

    # Renderiza o template de login
    # As mensagens adicionadas com messages.error/success no POST estarão disponíveis aqui
    return render(request, 'users/login.html')


# --- As views de cadastro e logout permanecem as mesmas ---

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Sua conta foi criada com sucesso! Por favor, faça login.')
            return redirect('users:login') # Use o name definido na URL
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu da sua conta.')
    return redirect('users:login') # Ou reverse('reviews:all_reviews') ou '/'