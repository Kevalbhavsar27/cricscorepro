from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('add/', views.team_add, name='team_add'),
    path('edit/<int:id>/', views.team_edit, name='team_edit'),
    path('delete/<int:id>/', views.team_delete, name='team_delete'),
]