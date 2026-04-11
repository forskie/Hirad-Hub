from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Favorite
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from library.models import Like, Comment
from user.models import CustomUser
from library.models import Topic
from django.core.paginator import Paginator


VALID_POST_TYPES = {'post', 'question', 'article'}

def post_list(request):
    topic_slug = request.GET.get('topic')
    post_type  = request.GET.get('type')
 
    posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('topics', 'likes', 'comments')
        .order_by('-created_at')
    )
 
    if topic_slug:
        posts = posts.filter(topics__slug=topic_slug)
 
    if post_type and post_type in VALID_POST_TYPES:
        posts = posts.filter(post_type=post_type)
 
    topics = Topic.objects.all()

    from django.db.models import Count
    all_posts = Post.objects.all()
    counts = {
        'post':     all_posts.filter(post_type='post').count(),
        'question': all_posts.filter(post_type='question').count(),
        'article':  all_posts.filter(post_type='article').count(),
    }
    unanswered_count = all_posts.filter(post_type='question', is_answered=False).count()
    total_count = all_posts.count()

    paginator = Paginator(posts, 15)
    page_num  = request.GET.get('page', 1)
    posts     = paginator.get_page(page_num)
 
    from django.contrib.auth import get_user_model
    User = get_user_model()
    top_users = User.objects.order_by('-score')[:5]
 
    return render(request, 'post/list.html', {
        'posts': posts,
        'topics': topics,
        'top_users': top_users,
        'counts': counts,
        'unanswered_count': unanswered_count,
        'total_count': total_count,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('topics'), pk=pk)
    post.increment_views()
    comments = post.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    liked = False
    other_posts = Post.objects.filter(author=post.author).exclude(pk=post.pk).order_by('-created_at')[:5]
    if request.user.is_authenticated:
        ct = ContentType.objects.get_for_model(Post)
        liked = Like.objects.filter(user=request.user, content_type=ct, object_id=post.pk).exists()
    return render(request, 'post/detail.html', {'post': post, 'comments': comments, 'liked': liked, 'other_posts': other_posts})

@login_required
def post_create(request):
    topics = Topic.objects.all()
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        topics_ids = request.POST.getlist('topics')
        if not text and not image and not video:
            return render(request, 'post/create.html', {
                'error': "Post cannot be empty.",
                'topics': topics
            })
        post_type = request.POST.get('post_type', 'post')
        post = Post.objects.create(author=request.user, text=text, image=image, video=video, post_type=post_type)
        
        if topics_ids:
            post.topics.set(topics_ids)
        return redirect('post:detail', pk=post.pk)
    return render(request, 'post/create.html', {
        'topics': topics
    })
    
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('post:list')
    return render(request, 'post/confirm_delete.html', {'post': post})

@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ct = ContentType.objects.get_for_model(Post)
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=post.pk
    )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    likes_count = Like.objects.filter(
        content_type=ct,
        object_id=post.pk
    ).count()
    if request.headers.get('HX-Request'):
        return render(
            request,
            'post/partials/like_button.html',
            {
                'liked': liked,
                'likes_count': likes_count,
                'post': post
            }
        )
    return redirect(request.META.get('HTTP_REFERER', 'post:list'))

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        if text:
            Comment.objects.create(
                user=request.user,
                content_object=post,
                text=text,
                parent_id=parent_id or None
            )
    if request.headers.get('HX-Request'):
        comments = post.comments.select_related('user').filter(parent=None).prefetch_related('replies')
        return render(request, 'post/partials/comments.html', {'post': post, 'comments': comments})
    return redirect('post:detail', pk=pk)
@login_required
def toggle_favorite(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ct = ContentType.objects.get_for_model(Post)
    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=post.pk
    )
    if not created:
        fav.delete()
        is_favorited = False
    else:
        is_favorited = True
    if request.headers.get('HX-Request'):
        return render(
            request,
            'post/partials/favorite_button.html',
            {
                'post': post,
                'is_favorited': is_favorited
            }
        )
    return redirect(request.META.get('HTTP_REFERER', 'post:list'))

def search_users(request):
    q = request.GET.get('q', '').strip()
    users = []
    if q:
        users = CustomUser.objects.filter(username__icontains=q).values('id', 'username', 'title', 'level', 'first_name', 'last_name')[:8]
    if request.headers.get('HX-Request'):
        return render(request, 'post/partials/user_search.html', {'users': users, 'q': q})
    return redirect('post:list')
