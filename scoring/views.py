from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from matches.models import Match
from teams.models import Team
from players.models import Player
from .models import Innings, BallByBall
from points.models import PointsTable
from stats.models import PlayerStats
@login_required
def scoring_setup(request, match_id):
    match = get_object_or_404(Match, id=match_id, user=request.user)

    existing_innings = Innings.objects.filter(
        match=match,
        user=request.user,
        is_completed=False
    ).first()

    if existing_innings:
        return redirect('scoring_panel', innings_id=existing_innings.id)

    if match.status != 'Live':
        messages.error(request, "Start the match first.")
        return redirect('match_list')

    team_a_players = Player.objects.filter(user=request.user, team=match.team_a)
    team_b_players = Player.objects.filter(user=request.user, team=match.team_b)

    if request.method == "POST":
        batting_team_id = request.POST.get('batting_team')
        striker_id = request.POST.get('striker')
        non_striker_id = request.POST.get('non_striker')
        bowler_id = request.POST.get('bowler')

        batting_team = get_object_or_404(Team, id=batting_team_id, user=request.user)

        if batting_team.id == match.team_a.id:
            bowling_team = match.team_b
        elif batting_team.id == match.team_b.id:
            bowling_team = match.team_a
        else:
            messages.error(request, "Invalid batting team selected.")
            return redirect('scoring_setup', match_id=match.id)

        striker = get_object_or_404(Player, id=striker_id, user=request.user, team=batting_team)
        non_striker = get_object_or_404(Player, id=non_striker_id, user=request.user, team=batting_team)
        bowler = get_object_or_404(Player, id=bowler_id, user=request.user, team=bowling_team)

        if striker.id == non_striker.id:
            messages.error(request, "Striker and non-striker cannot be same.")
            return redirect('scoring_setup', match_id=match.id)

        innings_number = Innings.objects.filter(match=match, user=request.user).count() + 1

        if innings_number > 2:
            messages.error(request, "Both innings already completed.")
            return redirect('match_list')

        target = None

        if innings_number == 2:
            first_innings = Innings.objects.filter(
                match=match,
                user=request.user,
                innings_number=1
            ).first()

            if first_innings:
                target = first_innings.runs + 1

        innings = Innings.objects.create(
            user=request.user,
            match=match,
            innings_number=innings_number,
            batting_team=batting_team,
            bowling_team=bowling_team,
            striker=striker,
            non_striker=non_striker,
            current_bowler=bowler,
            target=target
        )

        messages.success(request, "Scoring setup completed.")
        return redirect('scoring_panel', innings_id=innings.id)

    return render(request, 'scoring/scoring_setup.html', {
        'match': match,
        'team_a_players': team_a_players,
        'team_b_players': team_b_players,
    })


@login_required
def scoring_panel(request, innings_id):
    innings = get_object_or_404(Innings, id=innings_id, user=request.user)

    balls = BallByBall.objects.filter(
        innings=innings,
        user=request.user
    ).order_by('-id')[:20]

    batting_players = Player.objects.filter(
        user=request.user,
        team=innings.batting_team
    )

    bowling_players = Player.objects.filter(
        user=request.user,
        team=innings.bowling_team
    )

    batting_scorecard = {}

    for ball in BallByBall.objects.filter(innings=innings).order_by('id'):
        batsman = ball.batsman

        if batsman:
            if batsman.id not in batting_scorecard:
                batting_scorecard[batsman.id] = {
                    'player': batsman,
                    'runs': 0,
                    'balls': 0,
                    'fours': 0,
                    'sixes': 0,
                    'out': 'Not Out',
                }

            if ball.extra_type not in ['Wide']:
                batting_scorecard[batsman.id]['balls'] += 1

            if ball.extra_type in ['None', 'No Ball']:
                batting_scorecard[batsman.id]['runs'] += ball.runs

            if ball.runs == 4:
                batting_scorecard[batsman.id]['fours'] += 1

            if ball.runs == 6:
                batting_scorecard[batsman.id]['sixes'] += 1

            if ball.is_wicket and ball.out_player:
                if ball.out_player.id == batsman.id:
                    batting_scorecard[batsman.id]['out'] = ball.wicket_type

    bowling_scorecard = {}

    for ball in BallByBall.objects.filter(innings=innings).order_by('id'):
        bowler = ball.bowler

        if bowler:
            if bowler.id not in bowling_scorecard:
                bowling_scorecard[bowler.id] = {
                    'player': bowler,
                    'balls': 0,
                    'runs': 0,
                    'wickets': 0,
                }

            if ball.is_legal_ball:
                bowling_scorecard[bowler.id]['balls'] += 1

            bowling_scorecard[bowler.id]['runs'] += ball.runs + ball.extra_runs

            if ball.is_wicket and ball.wicket_type not in ['Run Out']:
                bowling_scorecard[bowler.id]['wickets'] += 1

    need_new_bowler = False

    if innings.legal_balls > 0 and innings.legal_balls % 6 == 0 and not innings.is_completed:
        last_ball = BallByBall.objects.filter(
            innings=innings,
            user=request.user,
            is_legal_ball=True
        ).order_by('-id').first()

        if last_ball and innings.current_bowler == last_ball.bowler:
            need_new_bowler = True

    return render(request, 'scoring/scoring_panel.html', {
        'innings': innings,
        'balls': balls,
        'batting_players': batting_players,
        'bowling_players': bowling_players,
        'batting_scorecard': batting_scorecard.values(),
        'bowling_scorecard': bowling_scorecard.values(),
        'need_new_bowler': need_new_bowler,
    })

@login_required
def add_ball(request, innings_id):
    innings = get_object_or_404(Innings, id=innings_id, user=request.user)
    if innings.legal_balls > 0 and innings.legal_balls % 6 == 0:
        last_ball = BallByBall.objects.filter(
            innings=innings,
            user=request.user,
            is_legal_ball=True
        ).order_by('-id').first()

        if last_ball and innings.current_bowler == last_ball.bowler:
            messages.error(request, "Over completed. Please select a new bowler.")
            return redirect('change_bowler', innings_id=innings.id)

    if innings.is_completed:
        messages.error(request, "This innings is already completed.")
        return redirect('scoring_panel', innings_id=innings.id)
        
    if request.method == "POST":
        runs = int(request.POST.get('runs', 0))
        extra_type = request.POST.get('extra_type', 'None')
        extra_runs = int(request.POST.get('extra_runs', 0))
        is_wicket = request.POST.get('is_wicket') == 'yes'
        wicket_type = request.POST.get('wicket_type', 'None')
        out_player_id = request.POST.get('out_player')
        new_batsman_id = request.POST.get('new_batsman')

        is_legal_ball = True

        if extra_type in ['Wide', 'No Ball']:
            is_legal_ball = False

        if extra_type == 'Wide' and extra_runs == 0:
            extra_runs = 1

        if extra_type == 'No Ball' and extra_runs == 0:
            extra_runs = 1

        current_over = innings.legal_balls // 6
        current_ball = innings.legal_balls % 6 + 1

        if not is_legal_ball:
            current_ball = innings.legal_balls % 6

        out_player = None

        if is_wicket and out_player_id:
            out_player = get_object_or_404(
                Player,
                id=out_player_id,
                user=request.user,
                team=innings.batting_team
            )

        BallByBall.objects.create(
            user=request.user,
            innings=innings,
            over_number=current_over,
            ball_number=current_ball,
            batsman=innings.striker,
            bowler=innings.current_bowler,
            runs=runs,
            extra_type=extra_type,
            extra_runs=extra_runs,
            is_wicket=is_wicket,
            wicket_type=wicket_type if is_wicket else 'None',
            out_player=out_player,
            is_legal_ball=is_legal_ball,
            commentary=create_commentary(
                innings,
                runs,
                extra_type,
                extra_runs,
                is_wicket,
                wicket_type
            )
        )

        innings.runs += runs + extra_runs

        if is_legal_ball:
            innings.legal_balls += 1

        if is_wicket:
            innings.wickets += 1

            if out_player and innings.striker and out_player.id == innings.striker.id:
                if new_batsman_id:
                    innings.striker = get_object_or_404(
                        Player,
                        id=new_batsman_id,
                        user=request.user,
                        team=innings.batting_team
                    )

            elif out_player and innings.non_striker and out_player.id == innings.non_striker.id:
                if new_batsman_id:
                    innings.non_striker = get_object_or_404(
                        Player,
                        id=new_batsman_id,
                        user=request.user,
                        team=innings.batting_team
                    )

        if not is_wicket:
            if runs in [1, 3]:
                swap_strike(innings)

        if is_legal_ball and innings.legal_balls % 6 == 0:
            swap_strike(innings)

        check_innings_complete(innings)

        innings.save()

        if innings.is_completed:
            messages.success(request, "Innings completed.")
            if innings.innings_number == 1:
                return redirect('start_second_innings', match_id=innings.match.id)
            else:
                return redirect('finish_match', match_id=innings.match.id)

        messages.success(request, "Ball added successfully.")
        return redirect('scoring_panel', innings_id=innings.id)


@login_required
def undo_ball(request, innings_id):
    innings = get_object_or_404(Innings, id=innings_id, user=request.user)

    last_ball = BallByBall.objects.filter(
        innings=innings,
        user=request.user
    ).order_by('-id').first()

    if not last_ball:
        messages.error(request, "No ball to undo.")
        return redirect('scoring_panel', innings_id=innings.id)

    innings.runs -= last_ball.runs + last_ball.extra_runs

    if last_ball.is_legal_ball and innings.legal_balls > 0:
        innings.legal_balls -= 1

    if last_ball.is_wicket and innings.wickets > 0:
        innings.wickets -= 1

    innings.is_completed = False
    last_ball.delete()
    innings.save()

    messages.success(request, "Last ball removed.")
    return redirect('scoring_panel', innings_id=innings.id)


def swap_strike(innings):
    innings.striker, innings.non_striker = innings.non_striker, innings.striker


def create_commentary(innings, runs, extra_type, extra_runs, is_wicket, wicket_type):
    batsman = innings.striker.name if innings.striker else "Batsman"
    bowler = innings.current_bowler.name if innings.current_bowler else "Bowler"

    if is_wicket:
        return f"{bowler} to {batsman}, OUT! {wicket_type}"

    if extra_type != 'None':
        return f"{bowler} to {batsman}, {extra_runs} {extra_type}"

    if runs == 4:
        return f"{bowler} to {batsman}, FOUR!"
    elif runs == 6:
        return f"{bowler} to {batsman}, SIX!"
    elif runs == 0:
        return f"{bowler} to {batsman}, dot ball"
    else:
        return f"{bowler} to {batsman}, {runs} run(s)"

def check_innings_complete(innings):
    max_overs = innings.match.tournament.get_overs()

    if innings.wickets >= 10:
        innings.is_completed = True

    if max_overs and innings.legal_balls >= max_overs * 6:
        innings.is_completed = True

    if innings.target and innings.runs >= innings.target:
        innings.is_completed = True

@login_required
def end_innings(request, innings_id):
    innings = get_object_or_404(Innings, id=innings_id, user=request.user)

    innings.is_completed = True
    innings.save()

    messages.success(request, "Innings completed successfully.")

    if innings.innings_number == 1:
        return redirect('start_second_innings', match_id=innings.match.id)

    return redirect('finish_match', match_id=innings.match.id)


@login_required
def start_second_innings(request, match_id):
    match = get_object_or_404(Match, id=match_id, user=request.user)

    first_innings = Innings.objects.filter(
        match=match,
        user=request.user,
        innings_number=1
    ).first()

    if not first_innings:
        messages.error(request, "First innings not found.")
        return redirect('match_list')

    if not first_innings.is_completed:
        messages.error(request, "First innings is not completed.")
        return redirect('scoring_panel', innings_id=first_innings.id)

    second_innings = Innings.objects.filter(
        match=match,
        user=request.user,
        innings_number=2
    ).first()

    if second_innings:
        return redirect('scoring_panel', innings_id=second_innings.id)

    if first_innings.batting_team.id == match.team_a.id:
        batting_team = match.team_b
        bowling_team = match.team_a
    else:
        batting_team = match.team_a
        bowling_team = match.team_b

    batting_players = Player.objects.filter(user=request.user, team=batting_team)
    bowling_players = Player.objects.filter(user=request.user, team=bowling_team)

    if request.method == "POST":
        striker = get_object_or_404(
            Player,
            id=request.POST.get('striker'),
            user=request.user,
            team=batting_team
        )

        non_striker = get_object_or_404(
            Player,
            id=request.POST.get('non_striker'),
            user=request.user,
            team=batting_team
        )

        bowler = get_object_or_404(
            Player,
            id=request.POST.get('bowler'),
            user=request.user,
            team=bowling_team
        )

        if striker.id == non_striker.id:
            messages.error(request, "Striker and non-striker cannot be same.")
            return redirect('start_second_innings', match_id=match.id)

        innings = Innings.objects.create(
            user=request.user,
            match=match,
            innings_number=2,
            batting_team=batting_team,
            bowling_team=bowling_team,
            striker=striker,
            non_striker=non_striker,
            current_bowler=bowler,
            target=first_innings.runs + 1
        )

        messages.success(request, "Second innings started.")
        return redirect('scoring_panel', innings_id=innings.id)

    return render(request, 'scoring/start_second_innings.html', {
        'match': match,
        'first_innings': first_innings,
        'batting_team': batting_team,
        'bowling_team': bowling_team,
        'batting_players': batting_players,
        'bowling_players': bowling_players,
    })


@login_required
def finish_match(request, match_id):
    match = get_object_or_404(Match, id=match_id, user=request.user)

    first_innings = Innings.objects.filter(
        match=match,
        user=request.user,
        innings_number=1
    ).first()

    second_innings = Innings.objects.filter(
        match=match,
        user=request.user,
        innings_number=2
    ).first()

    if not first_innings or not second_innings:
        messages.error(request, "Both innings are required to finish match.")
        return redirect('match_list')

    if match.status == "Completed":
        messages.warning(request, "Match already completed.")
        return redirect('match_list')

    if second_innings.runs > first_innings.runs:
        match.winner = second_innings.batting_team
        wickets_left = 10 - second_innings.wickets
        match.result_text = f"{second_innings.batting_team.name} won by {wickets_left} wickets"

    elif first_innings.runs > second_innings.runs:
        match.winner = first_innings.batting_team
        run_margin = first_innings.runs - second_innings.runs
        match.result_text = f"{first_innings.batting_team.name} won by {run_margin} runs"

    else:
        match.winner = None
        match.result_text = "Match tied"

    match.status = "Completed"
    match.save()

    first_innings.is_completed = True
    second_innings.is_completed = True
    first_innings.save()
    second_innings.save()

    update_points_table(match, first_innings, second_innings)
    
    update_player_statistics(match, first_innings)
    update_player_statistics(match, second_innings)

    messages.success(request, "Match completed and points table updated.")
    return redirect('match_list')

def update_points_table(match, first_innings, second_innings):
    team_a = match.team_a
    team_b = match.team_b

    team_a_table, created = PointsTable.objects.get_or_create(
        user=match.user,
        tournament=match.tournament,
        team=team_a
    )

    team_b_table, created = PointsTable.objects.get_or_create(
        user=match.user,
        tournament=match.tournament,
        team=team_b
    )

    team_a_table.matches += 1
    team_b_table.matches += 1

    if match.winner:
        if match.winner == team_a:
            team_a_table.wins += 1
            team_a_table.points += 2
            team_b_table.losses += 1
        else:
            team_b_table.wins += 1
            team_b_table.points += 2
            team_a_table.losses += 1
    else:
        team_a_table.ties += 1
        team_b_table.ties += 1
        team_a_table.points += 1
        team_b_table.points += 1

    if first_innings.batting_team == team_a:
        team_a_table.runs_for += first_innings.runs
        team_a_table.balls_for += first_innings.legal_balls
        team_a_table.runs_against += second_innings.runs
        team_a_table.balls_against += second_innings.legal_balls

        team_b_table.runs_for += second_innings.runs
        team_b_table.balls_for += second_innings.legal_balls
        team_b_table.runs_against += first_innings.runs
        team_b_table.balls_against += first_innings.legal_balls
    else:
        team_b_table.runs_for += first_innings.runs
        team_b_table.balls_for += first_innings.legal_balls
        team_b_table.runs_against += second_innings.runs
        team_b_table.balls_against += second_innings.legal_balls

        team_a_table.runs_for += second_innings.runs
        team_a_table.balls_for += second_innings.legal_balls
        team_a_table.runs_against += first_innings.runs
        team_a_table.balls_against += first_innings.legal_balls

    team_a_table.calculate_nrr()
    team_b_table.calculate_nrr()

    team_a_table.save()
    team_b_table.save()

def update_player_statistics(match, innings):
    batting_stats = {}

    for ball in BallByBall.objects.filter(innings=innings):

        batsman = ball.batsman

        if batsman.id not in batting_stats:
            batting_stats[batsman.id] = {
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
            }

        if ball.extra_type != 'Wide':
            batting_stats[batsman.id]['balls'] += 1

        if ball.extra_type in ['None', 'No Ball']:
            batting_stats[batsman.id]['runs'] += ball.runs

        if ball.runs == 4:
            batting_stats[batsman.id]['fours'] += 1

        if ball.runs == 6:
            batting_stats[batsman.id]['sixes'] += 1

    for player_id, data in batting_stats.items():

        player = Player.objects.get(id=player_id)

        stats, created = PlayerStats.objects.get_or_create(
            user=match.user,
            player=player
        )

        stats.matches += 1
        stats.innings += 1

        stats.runs += data['runs']
        stats.balls += data['balls']

        stats.fours += data['fours']
        stats.sixes += data['sixes']

        if data['runs'] > stats.highest_score:
            stats.highest_score = data['runs']

        stats.save()

    bowling_stats = {}

    for ball in BallByBall.objects.filter(innings=innings):

        bowler = ball.bowler

        if bowler.id not in bowling_stats:
            bowling_stats[bowler.id] = {
                'balls': 0,
                'runs': 0,
                'wickets': 0,
            }

        if ball.is_legal_ball:
            bowling_stats[bowler.id]['balls'] += 1

        bowling_stats[bowler.id]['runs'] += (
            ball.runs + ball.extra_runs
        )

        if ball.is_wicket and ball.wicket_type != 'Run Out':
            bowling_stats[bowler.id]['wickets'] += 1

    for player_id, data in bowling_stats.items():

        player = Player.objects.get(id=player_id)

        stats, created = PlayerStats.objects.get_or_create(
            user=match.user,
            player=player
        )

        stats.bowling_balls += data['balls']
        stats.bowling_runs += data['runs']
        stats.wickets += data['wickets']

        if data['wickets'] > stats.best_bowling_wickets:
            stats.best_bowling_wickets = data['wickets']
            stats.best_bowling_runs = data['runs']

        stats.save()

@login_required
def change_bowler(request, innings_id):
    innings = get_object_or_404(Innings, id=innings_id, user=request.user)

    if innings.is_completed:
        messages.error(request, "Innings already completed.")
        return redirect('scoring_panel', innings_id=innings.id)

    bowling_players = Player.objects.filter(
        user=request.user,
        team=innings.bowling_team
    )

    last_ball = BallByBall.objects.filter(
        innings=innings,
        user=request.user,
        is_legal_ball=True
    ).order_by('-id').first()

    last_bowler = last_ball.bowler if last_ball else None

    if request.method == "POST":
        bowler_id = request.POST.get('bowler')

        new_bowler = get_object_or_404(
            Player,
            id=bowler_id,
            user=request.user,
            team=innings.bowling_team
        )

        if last_bowler and new_bowler.id == last_bowler.id:
            messages.error(request, "Same bowler cannot bowl two consecutive overs.")
            return redirect('change_bowler', innings_id=innings.id)

        innings.current_bowler = new_bowler
        innings.save()

        messages.success(request, "New bowler selected.")
        return redirect('scoring_panel', innings_id=innings.id)

    return render(request, 'scoring/change_bowler.html', {
        'innings': innings,
        'bowling_players': bowling_players,
        'last_bowler': last_bowler,
    })