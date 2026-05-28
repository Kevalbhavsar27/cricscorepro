from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tournament


@login_required
def tournament_list(request):
    tournaments = Tournament.objects.filter(
        user=request.user
    ).order_by('-id')

    return render(request, 'tournaments/tournament_list.html', {
        'tournaments': tournaments
    })


@login_required
def tournament_add(request):
    if request.method == "POST":
        match_type = request.POST.get('match_type')
        custom_overs = request.POST.get('custom_overs')

        if match_type == 'CUSTOM':
            if not custom_overs:
                messages.error(request, "Please enter custom overs.")
                return redirect('tournament_add')
        else:
            custom_overs = None

        Tournament.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            location=request.POST.get('location'),
            match_type=match_type,
            custom_overs=custom_overs,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            status=request.POST.get('status')
        )

        messages.success(request, "Tournament added successfully.")
        return redirect('tournament_list')

    return render(request, 'tournaments/tournament_form.html')


@login_required
def tournament_edit(request, id):
    tournament = get_object_or_404(
        Tournament,
        id=id,
        user=request.user
    )

    if request.method == "POST":
        match_type = request.POST.get('match_type')
        custom_overs = request.POST.get('custom_overs')

        if match_type == 'CUSTOM':
            if not custom_overs:
                messages.error(request, "Please enter custom overs.")
                return redirect('tournament_edit', id=tournament.id)
        else:
            custom_overs = None

        tournament.name = request.POST.get('name')
        tournament.location = request.POST.get('location')
        tournament.match_type = match_type
        tournament.custom_overs = custom_overs
        tournament.start_date = request.POST.get('start_date')
        tournament.end_date = request.POST.get('end_date')
        tournament.status = request.POST.get('status')
        tournament.save()

        messages.success(request, "Tournament updated successfully.")
        return redirect('tournament_list')

    return render(request, 'tournaments/tournament_form.html', {
        'tournament': tournament
    })


@login_required
def tournament_delete(request, id):
    tournament = get_object_or_404(
        Tournament,
        id=id,
        user=request.user
    )

    tournament.delete()
    messages.success(request, "Tournament deleted successfully.")
    return redirect('tournament_list')