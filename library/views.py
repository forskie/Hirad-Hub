from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Video, Podcast, Topic, LibraryInteraction, Like, Comment
from django.contrib.contenttypes.models import ContentType

