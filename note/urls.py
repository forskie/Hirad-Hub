from django.urls import path
from . import views

app_name = 'note'

urlpatterns = [
    path('', views.note_list, name='list'),
    path('create', views.note_create, name='create'),
    path('<int:pk>/edit', views.note_edit, name='edit'),
    path('<int:pk>/delete', views.note_delete, name='delete'),
    path('<int:pk>', views.note_detail, name='detail'),
    path('toggle_like/<int:pk>', views.toggle_like, name='toggle_like'),
    path('<int:pk>/add_comment', views.add_comment, name='add_comment'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<int:pk>/delete/', views.delete_folder, name='delete_folder'),
    path('<int:pk>/move/', views.move_to_folder, name='move_to_folder'),
]

