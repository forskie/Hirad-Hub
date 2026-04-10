from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dashboard
from post.models import Post
from library.models import Book, Video, Podcast
from note.models import Note


from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q

User = get_user_model()

@login_required
def dashboard(request):
    dash, _ = Dashboard.objects.get_or_create(user=request.user)
    rank = User.objects.filter(score__gt=request.user.score).count() + 1
    top_users = User.objects.order_by('-score')[:5]
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    return render(request, 'main/dashboard.html',
                {'dash': dash, 
                'rank': rank,
                'top_users': top_users,
                'recent_posts': recent_posts
                })


def home(request):
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    ctx = {'recent_posts': recent_posts}
    
    if request.user.is_authenticated:
        from roadmap.models import UserProgress, Roadmap
 
        last_progress = (
            UserProgress.objects
            .filter(user=request.user, completed=False)
            .select_related('step__roadmap')
            .order_by('step__roadmap__id', 'step__order')
            .first()
        )
        ctx['current_step'] = last_progress.step if last_progress else None
 
        if request.user.role in ('teacher', 'director', 'admin'):
            ctx['teacher_books_count'] = Book.objects.filter(creator=request.user).count()
            ctx['teacher_videos_count'] = Video.objects.filter(creator=request.user).count()
            ctx['teacher_podcasts_count'] = Podcast.objects.filter(creator=request.user).count()
 
    return render(request, 'main/home.html', ctx)


def leaderboard(request):
    tab = request.GET.get('tab', 'students')
    if tab == 'teachers':
        from user.models import TeacherProfile
        leaders = TeacherProfile.objects.filter(
            is_verified=True
        ).select_related('user').order_by('-teacher_score')[:50]
    else:
        leaders = User.objects.filter(
            role='student'
        ).order_by('-score')[:50]
    user_rank = None
    if request.user.is_authenticated:
        if tab == 'teachers' and request.user.role == 'teacher':
            try:
                my_score = request.user.teacher_profile.teacher_score
                user_rank = TeacherProfile.objects.filter(
                    teacher_score__gt=my_score, is_verified=True
                ).count() + 1
            except:
                pass
        else:
            user_rank = User.objects.filter(
                role='student', score__gt=request.user.score
            ).count() + 1
    return render(request, 'main/leaderboard.html', {
        'leaders':   leaders,
        'user_rank': user_rank,
        'tab':       tab,
    })

def search(request):
    q = request.GET.get('q', '').strip()
    fmt = request.GET.get('format')
    if not q:
        if fmt == 'json':
            return JsonResponse({'users': [], 'posts': [], 'books': [], 'videos': [], 'podcasts': [], 'notes': []})
        return render(request, 'main/search.html', {'q': q, 'results': {}})
    users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)).values('username', 'first_name', 'last_name', 'level', 'title')[:6]
    posts = Post.objects.filter(Q(text__icontains=q)).select_related('author').order_by('-created_at')[:6]
    notes = Note.objects.filter(Q(title__icontains=q) | Q(content__icontains=q), is_public=True).select_related('author').order_by('-created_at')[:6]
    books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q)).order_by('-created_at')[:6]

    if fmt == 'json':
        return JsonResponse({
            'users': [{
                'username': u['username'],
                'full_name': f"{u['first_name']} {u['last_name']}".strip(),
                'level': u['level'],
                'title': u['title']
            }
                for u in users  
            ],

            'posts': [{'id': p.pk, 'text': p.text[:60]}
                for p in posts
            ],
            'notes': [{
                'id': n.pk,
                'title': n.title,
            }
            for n in notes
            ],

            'books': [{
                'id': b.pk, 'title': b.title 
            }
            for b in books
            ],
        })
    return render(request, 'main/search.html', {'q': q, 
                                                'results': {
                                                                'users': users,
                                                                'posts': posts,
                                                                'notes': notes,
                                                                'books': books,
                                                            }})