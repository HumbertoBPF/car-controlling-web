from .views.viewsets import AdsViewSet, GameViewSet, ScoreViewSet, UserViewSet
from .views import general, account
from django.urls import path

urlpatterns = [
    path('dashboard', general.dashboard, name='dashboard'),
    path('account/signup-form', account.signup_form, name='signup-form'),
    path('account/login-form', account.login_form, name='login-form'),
    path('account/signup', account.signup, name='signup'),
    path('account/login', account.login, name='login'),
    path('account/logout', account.logout, name='logout'),
    path('rankings', general.rankings, name='rankings'),
    path('account/profile', account.profile, name='profile'),
    path('account/delete', account.delete_account, name='delete-account'),
    path('account/update-form', account.update_account_form, name='update-account-form'),
    path('account/update', account.update_account, name='update-account'),
    path('account/change-picture', account.change_picture, name='change-picture'),
    path('game-download', general.game_download, name='game-download'),
    path('api/scores', ScoreViewSet.as_view()),
    path('api/games', GameViewSet.as_view()),
    path('api/users', UserViewSet.as_view()),
    path('api/ads', AdsViewSet.as_view())
]
