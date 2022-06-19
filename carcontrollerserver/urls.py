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
    path('api/scores', ScoreViewSet.as_view()),
    path('api/games', GameViewSet.as_view())
]
