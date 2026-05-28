from django.urls import path
from . import views

urlpatterns = [
    path('', views.player_list, name='player_list'),
    path('add/', views.player_add, name='player_add'),
    path('edit/<int:id>/', views.player_edit, name='player_edit'),
    path('delete/<int:id>/', views.player_delete, name='player_delete'),
]