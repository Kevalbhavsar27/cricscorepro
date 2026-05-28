from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from tournaments.models import Tournament
from .models import PointsTable


@login_required
def points_table_list(request):
    tournaments = Tournament.objects.filter(user=request.user).order_by('-id')

    return render(request, 'points/points_table_list.html', {
        'tournaments': tournaments
    })


@login_required
def points_table_detail(request, tournament_id):
    tournament = get_object_or_404(
        Tournament,
        id=tournament_id,
        user=request.user
    )

    points_table = PointsTable.objects.filter(
        user=request.user,
        tournament=tournament
    ).select_related('team').order_by('-points', '-net_run_rate', '-wins')

    return render(request, 'points/points_table_detail.html', {
        'tournament': tournament,
        'points_table': points_table
    })