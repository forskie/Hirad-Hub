from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Favorite
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from library.models import Like, Comment


def post_list(request):
    posts = Post.objects.select_related('author').prefetch_related('topics', 'likes', 'comments').order_by('-created_at') 
    return render(request, 'post/list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('topics'), pk=pk)
    comments = post.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    return render(request, 'post/detail.html', {'post': post, 'comments': comments})

@login_required
def post_create(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        topics_ids = request.POST.getlist('topics')
        if not text and  not image and not video:
            return render(request, 'post/create.html', {'error': "Post cannot be empty."})
        post = Post.objects.create(author=request.user, text=text, image=image, video=video)
        if topics_ids:
            post.topics.set(topics_ids)
        return redirect('post:detail', pk=post.pk)
    return render(request, 'post/create.html')


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
    like, created = Like.objects.get_or_create(user=request.user, content_type=ct, object_id=post.pk)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'post:list'))

@login_required
def toggle_favorite(request, pk):
    post = get_object_or_404(Post, pk=pk)
    ct = ContentType.objects.get_for_model(Post)
    fav, created = Favorite.objects.get_or_create(user=request.user, content_type=ct, object_id=post.pk)
    if not created:
        fav.delete()
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
    return redirect('post:detail', pk=pk)
