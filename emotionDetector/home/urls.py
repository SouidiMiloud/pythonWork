from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),

    path('ws/video/', views.video_feed),

    path('profile', views.profile),
    path('addModerator', views.addModerator, name="addModerator"),
    path('viewData', views.viewData),
    path('calendar', views.calendar, name="calendar"),
    path('exportData', views.exportData, name="exportData"),
]