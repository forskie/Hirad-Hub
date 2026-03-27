from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Video, Podcast, Topic, LibraryInteraction, Like, Comment
from django.contrib.contenttypes.models import ContentType
from user.decorators import teacher_required

# ________________  Base View  _______________

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
        ct = ContentType.objects.get_for_model(Video)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=video.pk
        )        
    return render(request, 'library/video_detail.html', {'video': video, 'comments': comments, 'interaction': interaction})


def podcast_detail(request, pk):
    podcast = get_object_or_404(Podcast.objects.prefetch_related('topics'), pk=pk)
    comments = podcast.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Podcast)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=podcast.pk
        ) 
    return render(request, 'library/podcast_detail.html', {'podcast': podcast, 'comments': comments, 'interaction': interaction})


# ________________________  User Student login View _____________________

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
    like, created = Like.objects.get_or_create(user=request.user, content_type=ct, object_id=obj.pk)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'library:home'))


# _________________ User Teacher login View __________

@teacher_required
def add_book(request):
    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        pages = request.POST.get('pages') or None
        if pages:
            pages=int(pages)
        file_book = request.FILES.get('file')
        if not author or not file_book:
            return render(request, 'library/add_book.html', {'error': 'Author and book are required.'})
        book = Book.objects.create(
            author=author, 
            file=file_book, pages=pages
        )
        book.topics.set(topics_ids)
        return redirect('library:book_detail', pk=book.pk)
    return render(request, 'library/add_book.html')

@teacher_required
def edit_added_book(request, pk):
    book = get_object_or_404(Book,  pk=pk, creator=request.user)
    if request.method == 'POST':
        book.author = request.POST.get('author', book.author).strip()
        book.pages = request.POST.get('pages', book.pages).strip()
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('file'):
            book.file= request.FILES.get('file')
        book.save()
        if topics_ids:
            book.topics.set(topics_ids)
        return redirect('library:book_detail', pk=book.pk)
    return render(request, 'library/edit_books_inf.html', {'book': book})



@teacher_required
def upload_podcast(request):
    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        duration = request.POST.get('duration') or None
        if duration:
            duration = int(duration)
        audio_file = request.FILES.get('audio_file')
        thumbnail = request.FILES.get('thumbnail')
        if not author or not audio_file:
            return render(request, 'library/upload_podcast.html', {'error': 'Author and podcast(audio file) are required.'})
        podcast = Podcast.objects.create(
            author=author, audio_file=audio_file,
            thumbnail=thumbnail, duration=duration
        )
        podcast.topics.set(topics_ids)
        return redirect('library:podcast_detail', pk=podcast.pk)
    return render(request, 'library/upload_podcast.html')
    
@teacher_required
def edit_added_podcast(request, pk):
    podcast = get_object_or_404(Podcast,  pk=pk, creator=request.user)
    if request.method == 'POST':
        podcast.author = request.POST.get('author', podcast.author).strip()
        podcast.duration = request.POST.get('duration', podcast.duration).strip()
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('thumbnail'):
            podcast.thumbnail = request.FILES.get('thumbnail')
        if request.FILES.get('audio_file'):
            podcast.audio_file = request.FILES.get('audio_file')
        podcast.save()
        if topics_ids:
            podcast.topics.set(topics_ids)
        return redirect('library:podcast_detail', pk=podcast.pk)
    return render(request, 'library/edit_podcast_inf.html', {'podcast': podcast})


@teacher_required
def upload_video(request):
    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        duration = request.POST.get('duration') or None
        if duration:
            duration = int(duration)
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        if not author or not video_file:
            return render(request, 'library/upload_video.html', {'error': 'Author and video (video file) are required.'})
        video = Video.objects.create(
            author=author, video_file=video_file,
            thumbnail=thumbnail, duration=duration
        )
        video.topics.set(topics_ids)
        return redirect('library:video_detail', pk=video.pk)
    return render(request, 'library/upload_video.html')


@teacher_required
def edit_added_video(request, pk):
    video = get_object_or_404(Video,  pk=pk, creator=request.user)
    if request.method == 'POST':
        video.author = request.POST.get('author', video.author).strip()
        video.duration = request.POST.get('duration', video.duration).strip()
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('thumbnail'):
            video.thumbnail = request.FILES.get('thumbnail')
        if request.FILES.get('video_file'):
            video.video_file = request.FILES.get('video_file')
        video.save()
        if topics_ids:
            video.topics.set(topics_ids)
        return redirect('library:video_detail', pk=video.pk)
    return render(request, 'library/edit_video_inf.html', {'video': video})
