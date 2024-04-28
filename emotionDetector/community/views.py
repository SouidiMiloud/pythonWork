from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_user(request):
    if request.user.is_authenticated:
        print('already authenticated')
        return redirect('home')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print('correct')
            login(request, user)
            return redirect('home')
        else:
            print('incorrect!!!!!!!')
            messages.success(request, ("there was an error, please try again"))
            return redirect('login')
    else:
        return render(request, 'registration/login.html', {})

def logout_user(request):
    logout(request)
    return redirect('login')