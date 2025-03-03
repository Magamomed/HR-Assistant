from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            user = authenticate(request, username=user.email, password=password)
            if user:
                login(request, user)
                print(f"[INFO] Пользователь {email} вошел в систему")
                return redirect("dashboard")
            else:
                messages.error(request, "Неверный пароль")
                print(f"[ERROR] Ошибка входа для {email}: неправильный пароль")
        else:
            messages.error(request, "Пользователь с таким email не найден")
            print(f"[WARNING] Попытка входа с несуществующим email: {email}")

    return render(request, "users/login.html")


# Выход из системы
def user_logout(request):
    user = request.user
    print(f"[INFO] Пользователь {user.email} вышел из системы")
    logout(request)
    return redirect("login")
