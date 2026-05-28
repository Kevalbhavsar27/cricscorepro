from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tournaments.models import Tournament
from .models import Team


@login_required
def team_list(request):
    teams = Team.objects.filter(user=request.user).select_related('tournament').order_by('-id')

    return render(request, 'teams/team_list.html', {
        'teams': teams
    })


@login_required
def team_add(request):
    tournaments = Tournament.objects.filter(user=request.user).order_by('-id')

    if request.method == "POST":
        tournament_id = request.POST.get('tournament')
        tournament = get_object_or_404(Tournament, id=tournament_id, user=request.user)

        Team.objects.create(
            user=request.user,
            tournament=tournament,
            name=request.POST.get('name'),
            short_name=request.POST.get('short_name'),
            city=request.POST.get('city'),
            captain_name=request.POST.get('captain_name'),
            coach_name=request.POST.get('coach_name'),
            logo=request.FILES.get('logo')
        )

        messages.success(request, "Team added successfully.")
        return redirect('team_list')

    return render(request, 'teams/team_form.html', {
        'tournaments': tournaments
    })


@login_required
def team_edit(request, id):
    team = get_object_or_404(Team, id=id, user=request.user)
    tournaments = Tournament.objects.filter(user=request.user).order_by('-id')

    if request.method == "POST":
        tournament_id = request.POST.get('tournament')
        tournament = get_object_or_404(Tournament, id=tournament_id, user=request.user)

        team.tournament = tournament
        team.name = request.POST.get('name')
        team.short_name = request.POST.get('short_name')
        team.city = request.POST.get('city')
        team.captain_name = request.POST.get('captain_name')
        team.coach_name = request.POST.get('coach_name')

        if request.FILES.get('logo'):
            team.logo = request.FILES.get('logo')

        team.save()

        messages.success(request, "Team updated successfully.")
        return redirect('team_list')

    return render(request, 'teams/team_form.html', {
        'team': team,
        'tournaments': tournaments
    })


@login_required
def team_delete(request, id):
    team = get_object_or_404(Team, id=id, user=request.user)
    team.delete()

    messages.success(request, "Team deleted successfully.")
    return redirect('team_list')