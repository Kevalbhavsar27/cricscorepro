from django.urls import path
from . import views

urlpatterns = [
    path('', views.points_table_list, name='points_table_list'),
    path('<int:tournament_id>/', views.points_table_detail, name='points_table_detail'),
]