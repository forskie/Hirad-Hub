from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.library_home, name='home'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    path('podcasts/<int:pk>/', views.podcast_detail, name='podcast_detail'),
    path('update_progress/<str:model_name>/<int:pk>/', views.update_progress, name='update_progress'),
    path('add_book/', views.add_book, name='add_book'),
    path('edit_book/<int:pk>/', views.edit_added_book, name='edit_book'),
    path('add_video/', views.upload_video, name='add_video'),
    path('edit_video/<int:pk>/', views.edit_added_video, name='edit_video'),
    path('add_podcast/', views.upload_podcast, name='add_podcast'),
    path('edit_podcast/<int:pk>/', views.edit_added_podcast, name='edit_podcast'),
]