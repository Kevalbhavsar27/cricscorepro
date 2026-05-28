from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from tournaments.models import Tournament
from teams.models import Team
from players.models import Player
from matches.models import Match


@login_required
def dashboard_view(request):
    context = {
        "total_tournaments": Tournament.objects.filter(user=request.user).count(),
        "total_teams": Team.objects.filter(user=request.user).count(),
        "total_players": Player.objects.filter(user=request.user).count(),
        "total_matches": Match.objects.filter(user=request.user).count(),
        "live_matches": Match.objects.filter(user=request.user, status='Live').count(),
        "completed_matches": Match.objects.filter(user=request.user, status='Completed').count(),
    }

    return render(request, "dashboard/dashboard.html", context)