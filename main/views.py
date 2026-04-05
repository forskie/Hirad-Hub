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
    rank = Dashboard.objects.filter(score__gt=request.user.score).count() + 1
    top_users = Dashboard.objects.order_by('-score')[:5]
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    return render(request, 'main/dashboard.html',
                {'dash': dash, 
                'rank': rank,
                'top_users': top_users,
                'recent_posts': recent_posts
                })


def home(request):
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    return render(request, 'main/home.html', {'recent_posts' : recent_posts})


def leaderboard(request):
    leaders = User.objects.order_by('-score').select_related('teacher_profile')[:50]
    user_rank = None
    if request.user.is_authenticated:
        user_rank = User.objects.filter(score__gt=request.user.score).count() + 1
    return render(request, 'main/leaderboard.html', {'leaders': leaders, 'user_rank': user_rank})


def search(request):
    q = request.GET.get('q', '').strip()
    fmt = request.GET.get('format')
    if not q:
        if fmt == 'json':
            return JsonResponse({'users': [], 'posts': [], 'books': [], 'videos': [], 'podcasts': [], 'notes': []})
        return render(request, 'main/search.html', {'q': q, 'results': []})
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