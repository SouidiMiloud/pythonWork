from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('analyze', views.analyze, name="analyze"),

    path('ws/video/', views.video_feed),

    path('profile', views.profile),
    path('addModerator', views.addModerator, name="addModerator"),
    path('viewData', views.viewData),
    path('calendar', views.calendar, name="calendar"),
    path('exportData', views.exportData, name="exportData"),
    path('users', views.show_users, name="users"),
    path('emotions', views.show_emotions, name="emotions"),
    path('processed_users', views.processed_users, name="processes_users"),
]