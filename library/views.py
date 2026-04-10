from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Video, Podcast, Topic, LibraryInteraction, Like, Comment, Category
from django.contrib.contenttypes.models import ContentType
from user.decorators import teacher_required
from datetime import timedelta

# ________________  Base View  _______________

def library_home(request):
    category_slug = request.GET.get('category')
    topic_slug    = request.GET.get('topic')
    material_type = request.GET.get('type') 
    sort          = request.GET.get('sort', 'new')

    books    = Book.objects.select_related('category').prefetch_related('topics')
    videos   = Video.objects.select_related('category').prefetch_related('topics')
    podcasts = Podcast.objects.select_related('category').prefetch_related('topics')


    if category_slug:
        books    = books.filter(category__slug=category_slug)
        videos   = videos.filter(category__slug=category_slug)
        podcasts = podcasts.filter(category__slug=category_slug)

    if topic_slug:
        books    = books.filter(topics__slug=topic_slug)
        videos   = videos.filter(topics__slug=topic_slug)
        podcasts = podcasts.filter(topics__slug=topic_slug)

    if sort == 'popular':
        from django.db.models import Count
        books    = books.annotate(lc=Count('likes')).order_by('-lc')
        videos   = videos.annotate(lc=Count('likes')).order_by('-lc')
        podcasts = podcasts.annotate(lc=Count('likes')).order_by('-lc')
    else:
        books    = books.order_by('-created_at')
        videos   = videos.order_by('-created_at')
        podcasts = podcasts.order_by('-created_at')

    if material_type == 'book':
        videos = Video.objects.none()
        podcasts = Podcast.objects.none()
    elif material_type == 'video':
        books = Book.objects.none()
        podcasts = Podcast.objects.none()
    elif material_type == 'podcast':
        books = Book.objects.none()
        videos = Video.objects.none()

    categories = Category.objects.filter(parent=None).prefetch_related('children').order_by('order')
    topics     = Topic.objects.all()

    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()

    return render(request, 'library/home.html', {
        'books':           books,
        'videos':          videos,
        'podcasts':        podcasts,
        'topics':          topics,
        'categories':      categories,
        'active_category': active_category,
        'sort':            sort,
        'material_type':   material_type,
    })

    
def book_detail(request, pk):
    book = get_object_or_404(Book.objects.prefetch_related('topics'), pk=pk)
    comments = book.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Book)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=book.pk
        ) 
    return render(request, 'library/details/book_detail.html', {'book': book, 'comments': comments, 'interaction': interaction})


def video_detail(request, pk):
    video = get_object_or_404(Video.objects.prefetch_related('topics'), pk=pk)
    comments = video.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Video)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=video.pk
        )        
    return render(request, 'library/details/video_detail.html', {'video': video, 'comments': comments, 'interaction': interaction})


def podcast_detail(request, pk):
    podcast = get_object_or_404(Podcast.objects.prefetch_related('topics'), pk=pk)
    comments = podcast.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    interaction = None
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Podcast)
        interaction, _ = LibraryInteraction.objects.get_or_create(
            user=request.user, content_type=ct, object_id=podcast.pk
        ) 
    return render(request, 'library/details/podcast_detail.html', {'podcast': podcast, 'comments': comments, 'interaction': interaction})


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
def add_comment(request, model_name, pk):
    model_map = {'book': Book, 'video': Video, 'podcast': Podcast}
    model = model_map.get(model_name)
    if not model:
        return redirect('library:home')
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        if text:
            Comment.objects.create(
                user=request.user,
                text=text,
                parent_id=parent_id or None,
                content_object=obj
            )
    if request.headers.get('HX-Request'):
        comments = obj.comments.select_related('user')\
            .filter(parent=None)\
            .prefetch_related('replies')

        return render(request, 'library/partials/comments.html', {
            'obj': obj,
            'comments': comments,
            'model_name': model_name
        })
    return redirect(f'library:{model_name}_detail', pk=pk)


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
    if request.headers.get('HX-Request'):
        return render(request, 'library/partials/like_button.html', {'obj': obj, 'model_name': model_name})
    return redirect(request.META.get('HTTP_REFERER', 'library:home'))


# _________________ User Teacher login View __________
@teacher_required
def add_book(request):
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    topics = Topic.objects.all()
    grades = range(1, 12)

    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        pages = request.POST.get('pages') or None
        file_book = request.FILES.get('file')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        level = request.POST.get('level', '')
        category_id = request.POST.get('category')
        grade = request.POST.get('grade')

        if pages:
            pages = int(pages)

        if not title or not author or not file_book:
            return render(request, 'library/uploads/add_book.html', {
                'error': 'Title, author and file are required.',
                'categories': categories,
                'topics': topics,
                'grades': grades
            })

        book = Book.objects.create(
            title=title,
            description=description,
            level=level,
            author=author,
            file=file_book,
            pages=pages,
            creator=request.user,
            category_id=category_id or None,
            grade=grade or None
        )

        book.topics.set(topics_ids)

        return redirect('library:book_detail', pk=book.pk)

    return render(request, 'library/uploads/add_book.html', {
        'categories': categories,
        'topics': topics,
        'grades': grades,
    })

@teacher_required
def edit_added_book(request, pk):
    book = get_object_or_404(Book, pk=pk, creator=request.user)
    if request.method == 'POST':
        book.author = request.POST.get('author', book.author).strip()
        pages = request.POST.get('pages')
        if pages:
            book.pages = int(pages)
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('file'):
            book.file = request.FILES.get('file')
        book.save()
        if topics_ids:
            book.topics.set(topics_ids)
        return redirect('library:book_detail', pk=book.pk)
    return render(request, 'library/edits/edit_books_inf.html', {'book': book})


@teacher_required
def upload_podcast(request):
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    topics = Topic.objects.all()
    grades = range(1, 12)

    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        duration = request.POST.get('duration')
        audio_file = request.FILES.get('audio_file')
        thumbnail = request.FILES.get('thumbnail')
        category_id = request.POST.get('category')
        grade = request.POST.get('grade')

        if duration:
            try:
                h, m, s = map(int, duration.split(':'))
                duration = timedelta(hours=h, minutes=m, seconds=s)
            except:
                duration = None

        if not author or not audio_file:
            return render(request, 'library/uploads/upload_podcast.html', {
                'error': 'Author and podcast(audio file) are required.',
                'categories': categories,
                'topics': topics,
                'grades': grades
            })

        podcast = Podcast.objects.create(
            author=author,
            audio_file=audio_file,
            thumbnail=thumbnail,
            duration=duration,
            creator=request.user,
            category_id=category_id or None,
            grade=grade or None
        )
        podcast.topics.set(topics_ids)
        return redirect('library:podcast_detail', pk=podcast.pk)
    return render(request, 'library/uploads/upload_podcast.html', {
        'categories': categories,
        'topics': topics,
        'grades': grades,
    })
    

@teacher_required
def edit_added_podcast(request, pk):
    podcast = get_object_or_404(Podcast,  pk=pk, creator=request.user)
    if request.method == 'POST':
        podcast.author = request.POST.get('author', podcast.author).strip()
        podcast.duration = request.POST.get('duration') or podcast.duration
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('thumbnail'):
            podcast.thumbnail = request.FILES.get('thumbnail')
        if request.FILES.get('audio_file'):
            podcast.audio_file = request.FILES.get('audio_file')
        podcast.save()
        if topics_ids:
            podcast.topics.set(topics_ids)
        return redirect('library:podcast_detail', pk=podcast.pk)
    return render(request, 'library/edits/edit_podcast_inf.html', {'podcast': podcast})

@teacher_required
def upload_video(request):
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    topics = Topic.objects.all()
    grades = range(1, 12)

    if request.method == 'POST':
        author = request.POST.get('author', '').strip()
        topics_ids = request.POST.getlist('topics')
        duration = request.POST.get('duration')
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        category_id = request.POST.get('category')
        grade = request.POST.get('grade')
        if duration:
            try:
                h, m, s = map(int, duration.split(':'))
                duration = timedelta(hours=h, minutes=m, seconds=s)
            except:
                duration = None
        if not author or not video_file:
            return render(request, 'library/uploads/upload_video.html', {
                'error': 'Author and video (video file) are required.',
                'categories': categories,
                'topics': topics,
                'grades': grades
            })
        video = Video.objects.create(
            author=author,
            video_file=video_file,
            thumbnail=thumbnail,
            duration=duration,
            creator=request.user,
            category_id=category_id or None,
            grade=grade or None
        )
        video.topics.set(topics_ids)
        return redirect('library:video_detail', pk=video.pk)
    return render(request, 'library/uploads/upload_video.html', {
        'categories': categories,
        'topics': topics,
        'grades': grades,
    })


@teacher_required
def edit_added_video(request, pk):
    video = get_object_or_404(Video,  pk=pk, creator=request.user)
    if request.method == 'POST':
        video.author = request.POST.get('author', video.author).strip()
        video.duration = request.POST.get('duration') or video.duration

        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('thumbnail'):
            video.thumbnail = request.FILES.get('thumbnail')
        if request.FILES.get('video_file'):
            video.video_file = request.FILES.get('video_file')
        video.save()
        if topics_ids:
            video.topics.set(topics_ids)
        return redirect('library:video_detail', pk=video.pk)
    return render(request, 'library/edits/edit_video_inf.html', {'video': video})
