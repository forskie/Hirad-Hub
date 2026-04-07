from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.register_choice, name='register'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/pending', views.pending_verification, name='pending_verification'),

    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view_others, name='profile_others'),
    
]
