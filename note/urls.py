from django.urls import path
from . import views

app_name = 'note'

urlpatterns = [
    path('', views.note_list, name='list'),
    path('create', views.note_create, name='note_create'),
    path('<str:note>/edit', views.note_edit, name='note_edit'),
    path('<str:note>/delete', views.note_delete, name='note_delete'),
    path('<str:note>', views.note_detail, name='note_detail'),
]

