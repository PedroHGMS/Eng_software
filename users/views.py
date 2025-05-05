from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('email')
        senha = request.POST.get('senha')

        User = get_user_model()

        try:
            user_obj = User.objects.get(username=identificador)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(email=identificador)
            except User.DoesNotExist:
                user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=senha)
        else:
            user = None

        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'reviews:all_reviews'))

        messages.error(request, 'Email ou senha inválidos.')
        return redirect('login')

    return render(request, 'users/login.html')
