from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dashboard
from post.models import Post
from library.models import Book, Video, Podcast
from note.models import Note
from roadmap.models import Roadmap


from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q

User = get_user_model()

@login_required
def dashboard(request):
    from user.models import DirectorProfile

    dash, _ = Dashboard.objects.get_or_create(user=request.user)
    user = request.user
    ctx = {
        'dash': dash,
        # "Top students" should only contain students (not teachers/directors/admins)
        'top_users': User.objects.filter(role='student').order_by('-score')[:5],
        'recent_posts': Post.objects.filter(author=user).order_by('-created_at')[:5],
    }
    if user.role == 'director':
        ctx['rank'] = None
        try:
            ctx['director_profile'] = user.director_profile
        except DirectorProfile.DoesNotExist:
            ctx['director_profile'] = None
    else:
        ctx['rank'] = User.objects.filter(score__gt=user.score).count() + 1
        ctx['director_profile'] = None
    return render(request, 'main/dashboard.html', ctx)


def home(request):
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    ctx = {'recent_posts': recent_posts}
    
    if request.user.is_authenticated:
        from roadmap.models import UserProgress, Roadmap
        from user.models import DirectorProfile

        if request.user.role == 'director':
            try:
                ctx['director_profile'] = request.user.director_profile
            except DirectorProfile.DoesNotExist:
                ctx['director_profile'] = None

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
            return JsonResponse({'users': [], 'posts': [], 'books': [], 'videos': [], 'podcasts': [], 'notes': [], 'roadmaps': []})
        return render(request, 'main/search.html', {'q': q, 'results': {}})
    users = User.objects.filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
    ).values('username', 'first_name', 'last_name', 'level', 'title', 'role')[:6]
    posts = Post.objects.filter(Q(text__icontains=q)).select_related('author').order_by('-created_at')[:6]
    notes = Note.objects.filter(Q(title__icontains=q) | Q(content__icontains=q), is_public=True).select_related('author').order_by('-created_at')[:6]
    books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q)).order_by('-created_at')[:6]
    roadmaps = Roadmap.objects.filter(
        Q(title__icontains=q) | Q(description__icontains=q),
        is_public=True,
    ).order_by('-created_at')[:6]

    if fmt == 'json':
        return JsonResponse({
            'users': [{
                'username': u['username'],
                'full_name': f"{u['first_name']} {u['last_name']}".strip(),
                'level': u['level'],
                'title': u['title'],
                'role': u['role'],
            }
                for u in users  
            ],

            'posts': [{'id': p.pk, 'text': p.text[:60]}
                for p in posts
            ],
            'roadmaps': [{
                'id': r.pk,
                'title': r.title,
            }
            for r in roadmaps
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
                                                                'roadmaps': roadmaps,
                                                                'notes': notes,
                                                                'books': books,
                                                            }})