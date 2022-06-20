from carcontrollerserver.viewsets import GameViewSet, ScoreViewSet
from . import views
from django.urls import path, include

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('account/signup-form', views.signup_form, name='signup-form'),
    path('account/login-form', views.login_form, name='login-form'),
    path('account/signup', views.signup, name='signup'),
    path('account/login', views.login, name='login'),
    path('account/logout', views.logout, name='logout'),
    path('rankings', views.rankings, name='rankings'),
    path('account/profile', views.profile, name='profile'),
    path('account/delete', views.delete_account, name='delete-account'),
    path('account/update-form', views.update_account_form, name='update-account-form'),
    path('account/update', views.update_account, name='update-account'),
    path('api/scores', ScoreViewSet.as_view()),
    path('api/games', GameViewSet.as_view())
]
