from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Video, Podcast, Topic, LibraryInteraction, Like, Comment
from django.contrib.contenttypes.models import ContentType


def library_home(request):
    topics = Topic.objects.all()
    books = Book.objects.prefetch_related('topics').order_by('-date_added')[:6]
    videos = Video.objects.prefetch_related('topics').order_by('-date_added')[:6]
    podcasts = Podcast.objects.prefetch_related('topics').order_by('-date_added')[:6]
    return render(request, 'library/home.html', {'topics': topics, 'books': books, 'videos': videos, 'podcasts': podcasts})


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.prefetch_related('topics'), pk=pk)
    comments = book.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Book)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=book.pk
        ) 
    return render(request, 'library/book_detail.html', {'book': book, 'comments': comments, 'interaction': interaction})


def video_detail(request, pk):
    video = get_object_or_404(Video.objects.prefetch_related('topics'), pk=pk)
    comments = video.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Book)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=video.pk
        )        
    return render(request, 'library/video_detail.html', {'video': video, 'comments': comments, 'interaction': interaction})


def podcast_detail(request, pk):
    podcast = get_object_or_404([Podcast].objects.prefetch_related('topics'), pk=pk)
    comments = podcast.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Book)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=podcast.pk
        ) 
    return render(request, 'library/podcast_detail.html', {'podcast': podcast, 'comments': comments, 'interaction': interaction})


@login_required
def update_progress(request, model_name, pk):
    model_map = {'book': Book, 'video': Video, 'podcast': Podcast}
    model = model_map.get(model_name)
    if not model:
        return redirect('library:home')
    obj = get_object_or_404(model, pk=pk)
    ct = ContentType.objects.get_for_model(model)
    interaction, _ = LibraryInteraction.objects.get_or_create(
        user=request.user, content_type=ct, object_id=obj.pk
    )
    if request.method == 'POST':
        progress = float(request.POST.get('progress', 0)) 
        interaction.progress = min(max(progress, 0.0), 100.0)
        interaction.completed = interaction.progress >= 100.0
        interaction.save()
    return redirect(request.META.get('HTTP_REFERER', 'library:home'))    


@login_required
def toggle_like(request, model_name, pk):
    model_map = {'book': Book, 'video': Video, 'podcast': Podcast}
    model = model_map.get(model_name)
    if not model:
        return redirect('library:home')
    obj = get_object_or_404(model, pk=pk)
    ct = ContentType.objects.get_for_model(model)
    like, created = Like.objects.get_or_create(user=request.user, content_type=ct, object_id=odj.pk)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'library:home'))