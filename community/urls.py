from django.urls import path, include
from . import views

app_name = 'community'


urlpatterns = [
    path('', views.community_list, name='list'),
    path('create/', views.community_create, name='create'),
    path('<slug:slug>/', views.community_detail, name='detail'),
    path('<slug:slug>/join/', views.community_join, name='join'),
    path('<slug:slug>/leave/', views.community_leave, name='leave'),
    path('<slug:slug>/delete/', views.community_delete, name='delete'),
    path('<slug:slug>/post/add/', views.community_post_add, name='post_add'),
    path('<slug:slug>/post/<int:cp_pk>/remove/', views.community_post_remove, name='post_remove'),
    path('<slug:slug>/approve/<int:user_pk>/', views.community_approve_member, name='approve_member'),
    path('<slug:slug>/reject/<int:user_pk>/', views.community_reject_member, name='reject_member'),
]