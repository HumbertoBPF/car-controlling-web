from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from application.forms import FormPicture
from application.utils import contains_parameters
from django.contrib.auth.models import User
from django.contrib import auth
from carcontrollerserver.models import AppUser, Game, Score
from django.contrib.auth.hashers import make_password
from carcontrollerserver.validators import is_valid_user_data


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
        if contains_parameters(request.POST, "email", "username", "password", "password_confirmation"):
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_confirmation = request.POST.get('password_confirmation')
            is_valid_data, error_msg = is_valid_user_data(email, username, password, password_confirmation)[0:2]
            if is_valid_data:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                app_user = AppUser(user = user)
                app_user.save()
                messages.success(request, "Account successfully created")
            else:
                messages.error(request, error_msg)
            return redirect('signup-form')
    return redirect('dashboard')


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('dashboard')


def profile(request):
    if request.method == "GET" and request.user.is_authenticated:
        if contains_parameters(request.GET, "game"):
            # If some game was specified in the GET parameters, show the scores of this game
            game = get_object_or_404(Game, game_tag = request.GET.get('game'))
        else:
            # If no game was specified in the GET parameters, use the first game
            game = Game.objects.first()
        scores = Score.objects.filter(game=game, user=request.user)
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
    return redirect('login-form')


def update_account_form(request):
    if request.user.is_authenticated:
        return render(request, 'update_account_form.html')
    return redirect('login-form')


def update_account(request):
    if request.method == "POST" and request.user.is_authenticated:
        if contains_parameters(request.POST, "email", "username", "password", "password_confirmation"):
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_confirmation = request.POST.get('password_confirmation')
            is_valid_data, error_msg = is_valid_user_data(email, username, password, password_confirmation, existing_user=request.user)[0:2]
            if is_valid_data:
                request.user.email = email
                request.user.username = username
                request.user.password = make_password(password)
                request.user.save() 
                # Login of the user with the new information(if it is not done, the user is automatically logged out)
                user = auth.authenticate(request, username = username, password = password)
                if user is not None:
                    auth.login(request, user)
                return redirect('profile')
            else:
                messages.error(request, error_msg)
            return redirect('update-account-form')
    return redirect('login-form')


def change_picture(request):
    if request.method == "POST" and request.user.is_authenticated:
        form_picture = FormPicture(request.POST, request.FILES)
        if form_picture.is_valid():
            app_user = get_object_or_404(AppUser, user = request.user)
            app_user.picture = form_picture.cleaned_data.get('picture')
            app_user.save()
            return redirect('profile')
        # Invalid form, return form with error message
        else:
            scores = Score.objects.filter(user=request.user)
            games = Game.objects.all()
            app_user = get_object_or_404(AppUser, user=request.user)
            return render(request, 'profile.html', {
                                                'scores': scores, 
                                                'games': games, 
                                                'selected_game': None, 
                                                'app_user': app_user,
                                                'form_picture': form_picture
                                            })
    return redirect('login-form')
