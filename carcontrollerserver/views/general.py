from django.shortcuts import get_object_or_404, redirect, render
from application.utils import contains_parameters
from django.db.models import Min
from carcontrollerserver.models import Game, Score

# Create your views here.
def dashboard(request):
    return render(request, 'index.html')

def rankings(request):
    if request.method == "GET":
        if contains_parameters(request.GET, "game"):
            game = get_object_or_404(Game, game_tag = request.GET.get('game'))
        else:
            game = Game.objects.first()
        # Return the best score of each player for the selected game
        scores = Score.objects.filter(game=game).values('user__username','game').annotate(score=Min('score')).order_by('score')
        # List of all the games for the select field of the form
        games = Game.objects.all()
        return render(request, 'rankings.html', {'scores': scores, 'games': games, 'selected_game': game})
    return redirect('dashboard')