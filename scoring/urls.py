from django.urls import path
from . import views

urlpatterns = [
    path('setup/<int:match_id>/', views.scoring_setup, name='scoring_setup'),
    path('score/<int:innings_id>/', views.scoring_panel, name='scoring_panel'),
    path('add-ball/<int:innings_id>/', views.add_ball, name='add_ball'),
    path('undo-ball/<int:innings_id>/', views.undo_ball, name='undo_ball'),

    path('end-innings/<int:innings_id>/', views.end_innings, name='end_innings'),
    path('start-second-innings/<int:match_id>/', views.start_second_innings, name='start_second_innings'),
    path('finish-match/<int:match_id>/', views.finish_match, name='finish_match'),

    path('change-bowler/<int:innings_id>/', views.change_bowler, name='change_bowler'),
]