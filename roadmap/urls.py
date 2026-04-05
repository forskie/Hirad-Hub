from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    path('', views.roadmap_list, name='list'),
    path('create/', views.roadmap_create, name='create'),
    path('<int:pk>/', views.roadmap_detail, name='detail'),
    path('<int:pk>/edit/', views.roadmap_edit, name='edit'),
    path('<int:pk>/delete/', views.roadmap_delete, name='delete'),
    path('step/<int:step_pk>/progress/', views.toggle_progress, name='toggle_progress'),
]