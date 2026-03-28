from django.urls import path
from . import views


app_name = 'main'   

urlpatterns = [
    path('', views.home, name='home'),
    path('/dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]