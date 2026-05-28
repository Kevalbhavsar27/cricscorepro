from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from tournaments.models import Tournament
from teams.models import Team
from .models import Match
from scoring.models import Innings, BallByBall
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
@login_required
def match_list(request):
    matches = Match.objects.filter(
        user=request.user
    ).select_related(
        'tournament',
        'team_a',
        'team_b',
        'toss_winner',
        'winner'
    ).order_by('-id')

    return render(request, 'matches/match_list.html', {
        'matches': matches
    })


@login_required
def match_add(request):
    tournaments = Tournament.objects.filter(user=request.user).order_by('-id')
    teams = Team.objects.filter(user=request.user).order_by('name')

    if request.method == "POST":
        tournament_id = request.POST.get('tournament')
        team_a_id = request.POST.get('team_a')
        team_b_id = request.POST.get('team_b')
        toss_winner_id = request.POST.get('toss_winner')

        tournament = get_object_or_404(
            Tournament,
            id=tournament_id,
            user=request.user
        )

        team_a = get_object_or_404(
            Team,
            id=team_a_id,
            user=request.user,
            tournament=tournament
        )

        team_b = get_object_or_404(
            Team,
            id=team_b_id,
            user=request.user,
            tournament=tournament
        )

        if team_a.id == team_b.id:
            messages.error(request, "Team A and Team B cannot be same.")
            return redirect('match_add')

        toss_winner = None
        if toss_winner_id:
            toss_winner = get_object_or_404(
                Team,
                id=toss_winner_id,
                user=request.user,
                tournament=tournament
            )

            if toss_winner.id not in [team_a.id, team_b.id]:
                messages.error(request, "Toss winner must be Team A or Team B.")
                return redirect('match_add')
            match = Match.objects.create(
                user=request.user,
                tournament=tournament,
                team_a=team_a,
                team_b=team_b,
                venue=request.POST.get('venue'),
                match_date=request.POST.get('match_date'),
                toss_winner=toss_winner,
                toss_decision=request.POST.get('toss_decision') or None,
                status=request.POST.get('status')
            )

            generate_match_qr(request, match)

        messages.success(request, "Match created successfully.")
        return redirect('match_list')

    return render(request, 'matches/match_form.html', {
        'tournaments': tournaments,
        'teams': teams
    })


@login_required
def match_edit(request, id):
    match = get_object_or_404(Match, id=id, user=request.user)

    tournaments = Tournament.objects.filter(user=request.user).order_by('-id')
    teams = Team.objects.filter(user=request.user).order_by('name')

    if request.method == "POST":
        tournament_id = request.POST.get('tournament')
        team_a_id = request.POST.get('team_a')
        team_b_id = request.POST.get('team_b')
        toss_winner_id = request.POST.get('toss_winner')
        winner_id = request.POST.get('winner')

        tournament = get_object_or_404(
            Tournament,
            id=tournament_id,
            user=request.user
        )

        team_a = get_object_or_404(
            Team,
            id=team_a_id,
            user=request.user,
            tournament=tournament
        )

        team_b = get_object_or_404(
            Team,
            id=team_b_id,
            user=request.user,
            tournament=tournament
        )

        if team_a.id == team_b.id:
            messages.error(request, "Team A and Team B cannot be same.")
            return redirect('match_edit', id=match.id)

        toss_winner = None
        if toss_winner_id:
            toss_winner = get_object_or_404(
                Team,
                id=toss_winner_id,
                user=request.user,
                tournament=tournament
            )

        winner = None
        if winner_id:
            winner = get_object_or_404(
                Team,
                id=winner_id,
                user=request.user,
                tournament=tournament
            )

        match.tournament = tournament
        match.team_a = team_a
        match.team_b = team_b
        match.venue = request.POST.get('venue')
        match.match_date = request.POST.get('match_date')
        match.toss_winner = toss_winner
        match.toss_decision = request.POST.get('toss_decision') or None
        match.status = request.POST.get('status')
        match.winner = winner
        match.result_text = request.POST.get('result_text')
        match.save()

        messages.success(request, "Match updated successfully.")
        return redirect('match_list')

    return render(request, 'matches/match_form.html', {
        'match': match,
        'tournaments': tournaments,
        'teams': teams
    })


@login_required
def match_delete(request, id):
    match = get_object_or_404(Match, id=id, user=request.user)
    match.delete()

    messages.success(request, "Match deleted successfully.")
    return redirect('match_list')


@login_required
def match_start(request, id):
    match = get_object_or_404(Match, id=id, user=request.user)

    if not match.toss_winner or not match.toss_decision:
        messages.error(request, "Please add toss winner and toss decision before starting match.")
        return redirect('match_edit', id=match.id)

    match.status = 'Live'
    match.save()

    messages.success(request, "Match started successfully. Setup scoring now.")
    return redirect('scoring_setup', match_id=match.id)

def public_match_score(request, id):
    match = get_object_or_404(Match, id=id)

    innings_list = Innings.objects.filter(
        match=match
    ).order_by('innings_number')

    current_innings = innings_list.filter(is_completed=False).first()
    if not current_innings:
        current_innings = innings_list.last()

    full_scorecards = []

    for innings in innings_list:
        full_scorecards.append({
            'innings': innings,
            'batting_scorecard': build_batting_scorecard(innings),
            'bowling_scorecard': build_bowling_scorecard(innings),
            'extras': build_extras_summary(innings),
            'fall_of_wickets': build_fall_of_wickets(innings),
        })

    recent_balls = []
    if current_innings:
        recent_balls = BallByBall.objects.filter(
            innings=current_innings
        ).order_by('-id')[:20]

    full_commentary = BallByBall.objects.filter(
        innings__match=match
    ).select_related(
        'innings',
        'batsman',
        'bowler'
    ).order_by('-id')

    return render(request, 'matches/public_match_score.html', {
        'match': match,
        'innings_list': innings_list,
        'current_innings': current_innings,
        'recent_balls': recent_balls,
        'full_scorecards': full_scorecards,
        'full_commentary': full_commentary,
    })


def build_batting_scorecard(innings):
    scorecard = {}

    for ball in BallByBall.objects.filter(innings=innings).order_by('id'):
        batsman = ball.batsman

        if not batsman:
            continue

        if batsman.id not in scorecard:
            scorecard[batsman.id] = {
                'player': batsman,
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
                'out': 'Not Out',
            }

        if ball.extra_type != 'Wide':
            scorecard[batsman.id]['balls'] += 1

        if ball.extra_type in ['None', 'No Ball']:
            scorecard[batsman.id]['runs'] += ball.runs

        if ball.runs == 4:
            scorecard[batsman.id]['fours'] += 1

        if ball.runs == 6:
            scorecard[batsman.id]['sixes'] += 1

        if ball.is_wicket and ball.out_player:
            if ball.out_player.id == batsman.id:
                scorecard[batsman.id]['out'] = ball.wicket_type

    return scorecard.values()


def build_bowling_scorecard(innings):
    scorecard = {}

    for ball in BallByBall.objects.filter(innings=innings).order_by('id'):
        bowler = ball.bowler

        if not bowler:
            continue

        if bowler.id not in scorecard:
            scorecard[bowler.id] = {
                'player': bowler,
                'balls': 0,
                'runs': 0,
                'wickets': 0,
            }

        if ball.is_legal_ball:
            scorecard[bowler.id]['balls'] += 1

        scorecard[bowler.id]['runs'] += ball.runs + ball.extra_runs

        if ball.is_wicket and ball.wicket_type != 'Run Out':
            scorecard[bowler.id]['wickets'] += 1

    return scorecard.values()


def build_extras_summary(innings):
    wides = 0
    no_balls = 0
    byes = 0
    leg_byes = 0

    balls = BallByBall.objects.filter(innings=innings)

    for ball in balls:
        if ball.extra_type == 'Wide':
            wides += ball.extra_runs
        elif ball.extra_type == 'No Ball':
            no_balls += ball.extra_runs
        elif ball.extra_type == 'Bye':
            byes += ball.extra_runs
        elif ball.extra_type == 'Leg Bye':
            leg_byes += ball.extra_runs

    total = wides + no_balls + byes + leg_byes

    return {
        'wides': wides,
        'no_balls': no_balls,
        'byes': byes,
        'leg_byes': leg_byes,
        'total': total,
    }


def build_fall_of_wickets(innings):
    wickets = []
    running_score = 0

    balls = BallByBall.objects.filter(
        innings=innings
    ).order_by('id')

    for ball in balls:
        running_score += ball.runs + ball.extra_runs

        if ball.is_wicket and ball.out_player:
            wickets.append({
                'score': running_score,
                'player': ball.out_player,
                'over': f"{ball.over_number}.{ball.ball_number}",
                'wicket_type': ball.wicket_type,
            })

    return wickets


def generate_match_qr(request, match):
    public_url = request.build_absolute_uri(
        f"/matches/public/{match.id}/"
    )

    qr = qrcode.make(public_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    filename = f"match_{match.id}_qr.png"

    match.qr_code.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=True
    )