from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login_user', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout")
]