from django.urls import path
from . import views

urlpatterns = [
    path('', views.stats_home, name='stats_home'),
    path('player/<int:player_id>/', views.player_stats, name='player_stats'),
]