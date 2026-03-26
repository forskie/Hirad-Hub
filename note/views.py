from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
        if not title or content:
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
        note.is_public = request.POST.get('is_public', note.title) == 'on'
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