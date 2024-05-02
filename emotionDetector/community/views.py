from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.models import ModeratorUser, Role


def is_admin(request):
    user = request.user
    is_admin_ = False
    if user.is_authenticated:
        moderator_user = ModeratorUser.objects.filter(email=user.email).first()
        if moderator_user and moderator_user.role == Role.ADMIN:
            is_admin_ = True
    return is_admin_

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        identity = request.POST["identity"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            role = ModeratorUser.objects.get(username=username).role
            if (identity == 'admin' and role == Role.MODERATOR) or (identity == 'moderator' and role == Role.ADMIN):
                return redirect('/')
            else: 
                login(request, user)
                return redirect('/')
        else:
            return redirect('/')
    else:
        identity = request.GET.get('identity')
        return render(request, 'registration/login.html', {'identity': identity, 'is_admin': is_admin(request)})

def logout_user(request):
    logout(request)
    return redirect('/')