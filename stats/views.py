from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from players.models import Player
from .models import PlayerStats


@login_required
def stats_home(request):

    top_batsmen = PlayerStats.objects.filter(
        user=request.user
    ).order_by('-runs')[:10]

    top_bowlers = PlayerStats.objects.filter(
        user=request.user
    ).order_by('-wickets')[:10]

    return render(request, 'stats/stats_home.html', {
        'top_batsmen': top_batsmen,
        'top_bowlers': top_bowlers,
    })


@login_required
def player_stats(request, player_id):
    player = get_object_or_404(
        Player,
        id=player_id,
        user=request.user
    )

    stats, created = PlayerStats.objects.get_or_create(
        user=request.user,
        player=player
    )

    return render(request, 'stats/player_stats.html', {
        'player': player,
        'stats': stats,
    })