from django.urls import path
from . import views

urlpatterns = [
    path('', views.tournament_list, name='tournament_list'),
    path('add/', views.tournament_add, name='tournament_add'),
    path('edit/<int:id>/', views.tournament_edit, name='tournament_edit'),
    path('delete/<int:id>/', views.tournament_delete, name='tournament_delete'),
]