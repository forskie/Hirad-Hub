from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('post/new/', views.post_create, name='create'),
    path('post/<int:pk>/delete/', views.post_delete, name='delete'),
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('search-users/', views.search_users, name='search_users'),
    
]