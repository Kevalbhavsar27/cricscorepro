from django import template

register = template.Library()


@register.filter
def balls_to_overs(balls):
    try:
        balls = int(balls)
        overs = balls // 6
        remaining_balls = balls % 6
        return f"{overs}.{remaining_balls}"
    except:
        return "0.0"


@register.filter
def strike_rate(runs, balls):
    try:
        runs = int(runs)
        balls = int(balls)

        if balls == 0:
            return "0.00"

        return f"{(runs / balls) * 100:.2f}"
    except:
        return "0.00"


@register.filter
def economy_rate(runs, balls):
    try:
        runs = int(runs)
        balls = int(balls)

        if balls == 0:
            return "0.00"

        return f"{(runs / balls) * 6:.2f}"
    except:
        return "0.00"