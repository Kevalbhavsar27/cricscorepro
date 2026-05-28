from django.urls import path
from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('add/', views.match_add, name='match_add'),
    path('edit/<int:id>/', views.match_edit, name='match_edit'),
    path('delete/<int:id>/', views.match_delete, name='match_delete'),
    path('start/<int:id>/', views.match_start, name='match_start'),

    path('public/<int:id>/', views.public_match_score, name='public_match_score'),
]