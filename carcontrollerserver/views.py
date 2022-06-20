from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from application.forms import FormPicture
from application.utils import contains_parameters
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Min
from carcontrollerserver.models import AppUser, Game, Score
from django.contrib.auth.hashers import make_password

# Create your views here.
def dashboard(request):
    return render(request, 'index.html')

def signup_form(request):
    return render(request, 'signup_form.html')

def login_form(request):
    return render(request, 'login_form.html')

def login(request):
    if request.method == "POST":
        if contains_parameters(request.POST, "username", "password"):
            username = request.POST.get('username')
            password = request.POST.get('password')
            if User.objects.filter(username=username).exists():
                user = auth.authenticate(request, username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return redirect('dashboard')
    messages.error(request, "Wrong credentials")
    return redirect('login-form')

def signup(request):
    if request.method == "POST":
        if contains_parameters(request.POST, "username", "password"):
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_confirmation = request.POST.get('password')
            if (" " in email) or (" " in username) or (" " in password):
                messages.error(request, "Fields cannot contain spaces")
            elif (len(email) == 0) or (len(username) == 0):
                messages.error(request, "All fields are required")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "This username is not available")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "This email is not available")
            elif len(password) < 6 or len(password) > 30:
                messages.error(request, "Password length out of range(passwords must be 6 and 30 characters long)")
            elif password != password_confirmation:
                messages.error(request, "The passwords do not match")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                app_user = AppUser(user = user)
                app_user.save()
                messages.success(request, "Account successfully created")
            return redirect('signup-form')
    return redirect('dashboard')

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('dashboard')

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

def profile(request):
    if request.method == "GET" and request.user.is_authenticated:
        if contains_parameters(request.GET, "game") and request.GET.get('game') != "all_games":
            game = get_object_or_404(Game, game_tag = request.GET.get('game'))
            scores = Score.objects.filter(game=game, user=request.user)
        else:
            game = None
            scores = Score.objects.filter(user=request.user)
        # List of all the games for the select field of the form
        games = Game.objects.all()
        app_user = get_object_or_404(AppUser, user=request.user)
        form_picture = FormPicture()
        return render(request, 'profile.html', {
                                                'scores': scores, 
                                                'games': games, 
                                                'selected_game': game, 
                                                'app_user': app_user,
                                                'form_picture': form_picture
                                            })
    return redirect('login-form')

def delete_account(request):
    if request.method == "POST" and request.user.is_authenticated:
        request.user.delete()
    return redirect('dashboard')

def update_account_form(request):
    if request.user.is_authenticated:
        return render(request, 'update_account_form.html')
    return redirect('login-form')

def update_account(request):
    if request.method == "POST" and request.user.is_authenticated:
        if contains_parameters(request.POST, "username", "password"):
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_confirmation = request.POST.get('password')
            if (" " in email) or (" " in username) or (" " in password):
                messages.error(request, "Fields cannot contain spaces")
            elif (len(email) == 0) or (len(username) == 0):
                messages.error(request, "All fields are required")
            elif request.user.username != username and User.objects.filter(username=username).exists():
                messages.error(request, "This username is not available")
            elif email!=request.user.email and User.objects.filter(email=email).exists():
                messages.error(request, "This email is not available")
            elif len(password) < 6 or len(password) > 30:
                messages.error(request, "Password length out of range(passwords must be 6 and 30 characters long)")
            elif password != password_confirmation:
                messages.error(request, "The passwords do not match")
            else:
                request.user.email = email
                request.user.username = username
                request.user.password = make_password(password)
                request.user.save() 
                # Login of the user with the new information(if it is not done, the user is automatically logged out)
                user = auth.authenticate(request, username = username, password = password)
                if user is not None:
                    auth.login(request, user)
                return redirect('profile')
            return redirect('update-account-form')
    return redirect('profile')

def change_picture(request):
    if request.method == "POST" and request.user.is_authenticated:
        form_picture = FormPicture(request.POST, request.FILES)
        if form_picture.is_valid():
            app_user = get_object_or_404(AppUser, user = request.user)
            app_user.picture = form_picture.cleaned_data.get('picture')
            app_user.save()
    return redirect('profile')