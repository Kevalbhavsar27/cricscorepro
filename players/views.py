from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from teams.models import Team
from .models import Player


@login_required
def player_list(request):
    players = Player.objects.filter(
        user=request.user
    ).select_related('team').order_by('-id')

    return render(request, 'players/player_list.html', {
        'players': players
    })


@login_required
def player_add(request):
    teams = Team.objects.filter(user=request.user)

    if request.method == "POST":
        team_id = request.POST.get('team')

        team = get_object_or_404(
            Team,
            id=team_id,
            user=request.user
        )

        Player.objects.create(
            user=request.user,
            team=team,
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            batting_style=request.POST.get('batting_style'),
            bowling_style=request.POST.get('bowling_style'),
            jersey_number=request.POST.get('jersey_number') or None,
            age=request.POST.get('age') or None,
            image=request.FILES.get('image')
        )

        messages.success(request, "Player added successfully.")
        return redirect('player_list')

    return render(request, 'players/player_form.html', {
        'teams': teams
    })


@login_required
def player_edit(request, id):
    player = get_object_or_404(
        Player,
        id=id,
        user=request.user
    )

    teams = Team.objects.filter(user=request.user)

    if request.method == "POST":
        team_id = request.POST.get('team')

        team = get_object_or_404(
            Team,
            id=team_id,
            user=request.user
        )

        player.team = team
        player.name = request.POST.get('name')
        player.role = request.POST.get('role')
        player.batting_style = request.POST.get('batting_style')
        player.bowling_style = request.POST.get('bowling_style')
        player.jersey_number = request.POST.get('jersey_number') or None
        player.age = request.POST.get('age') or None

        if request.FILES.get('image'):
            player.image = request.FILES.get('image')

        player.save()

        messages.success(request, "Player updated successfully.")
        return redirect('player_list')

    return render(request, 'players/player_form.html', {
        'player': player,
        'teams': teams
    })


@login_required
def player_delete(request, id):
    player = get_object_or_404(
        Player,
        id=id,
        user=request.user
    )

    player.delete()

    messages.success(request, "Player deleted successfully.")
    return redirect('player_list')