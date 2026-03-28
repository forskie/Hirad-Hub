from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from library.models import Comment, Like
from post.models import Post
from .models import Note

@login_required
def note_list(request):
    notes = Note.objects.filter(author=request.user).prefetch_related('topics').order_by('-created_at')
    return render(request, 'note/list.html', {'notes': notes})
    
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)    
    if not Note.can_view(request.user if request.user.is_authenticated else None, note):
        return redirect('note:list')
    comments = note.comments.select_related('user').filter(parent=None).prefetch_related('replies')
    return render(request, 'note/detail.html', {'note': note, 'comments': comments})

@login_required
def note_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_public = request.POST.get('is_public', '') == 'on'
        topics_ids = request.POST.getlist('topics')
        img = request.FILES.get('img')
        if not title or not content:
            return render(request, 'note/create.html', {'error': 'Title and content are required.'})
        note = Note.objects.create(
            author=request.user, title=title,
            content=content, is_public=is_public, img=img
        )
        
        if topics_ids:
            note.topics.set(topics_ids)
        return redirect('note:detail', pk=note.pk)
    return render(request, 'note/create.html')

@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)
    if request.method == 'POST':
        note.title = request.POST.get('title', note.title).strip()
        note.content = request.POST.get('content', note.content).strip()
        note.is_public = request.POST.get('is_public', '') == 'on'
        topics_ids = request.POST.getlist('topics')
        if request.FILES.get('img'):
            note.img = request.FILES.get('img')
        note.save()
        if topics_ids:
            note.topics.set(topics_ids)
        return redirect('note:detail', pk=note.pk)
    return render(request, 'note/edit.html', {'note': note})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, author=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note:list')
    return render(request, 'note/confirm_delete.html', {'note': note})



@login_required
def toggle_like(request, pk):
    note = get_object_or_404(Note, pk=pk)
    ct = ContentType.objects.get_for_model(Note)
    like, created = Like.objects.get_or_create(user=request.user, content_type=ct, object_id=note.pk)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'note:list'))


@login_required
def add_comment(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        if text:
            Comment.objects.create(
                user=request.user,  
                content_object=note,
                text=text,
                parent_id=parent_id or None
            )
    return redirect('note:detail', pk=pk)
    