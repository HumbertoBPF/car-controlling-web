from . import views
from django.urls import path, include

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard')
]
