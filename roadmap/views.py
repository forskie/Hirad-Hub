from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from .models import Roadmap, Step, StepResource, UserProgress
from django.utils import timezone

from library.models import Topic
from user.decorators import teacher_required


def roadmap_list(request):
    topic_slug = request.GET.get('topic')
    roadmaps = Roadmap.objects.filter(is_public=True).select_related('topic', 'creator').prefetch_related('steps')
    if topic_slug:
        roadmaps = roadmaps.filter(topic__slug=topic_slug)
    roadmaps = roadmaps.order_by('-created_at')
    topics = Topic.objects.all()
    return render(request, 'roadmap/list.html',
                  {'roadmaps': roadmaps, 
                   'topics': topics,
                   })


def roadmap_detail(request, pk):
    roadmap = get_object_or_404(Roadmap.objects.select_related('creator', 'topic'), pk=pk)

    if not roadmap.is_public and request.user != roadmap.creator:
        return redirect('roadmap:list')
    
    steps = roadmap.steps.prefetch_related('resources__content_type').order_by('order')
    user_progress = {}
    completed_count = None
    if request.user.is_authenticated:
        progress = UserProgress.objects.filter(user=request.user, step__roadmap=roadmap).select_related('step')
        user_progress = {p.step_id: p for p in progress}
        completed_count = sum(1 for p in progress if p.completed)


    return render(request, 'roadmap/detail.html',{
        'roadmap': roadmap,
        'steps': steps,
        'user_progress': user_progress,
        'completed_count': completed_count,
    })

@teacher_required
def roadmap_create(request):
    topics = Topic.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        topic_id = request.POST.get('topic') or None
        is_public = request.POST.get('is_public') == 'on'
        if not title:
            return render(request, 'roadmap/create.html', {'topics': topics, 'error': 'Title is required.', 'form': request.POST})
    
        roadmap = Roadmap.objects.create(
            title=title,
            description=description,
            topic_id=topic_id,
            creator=request.user,
            is_public=is_public
        )
        return redirect('roadmap:edit', pk=roadmap.pk)
    return render(request, 'roadmap/create.html', {'topics': topics})


@login_required
def roadmap_edit(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk, creator=request.user)
    topics = Topic.objects.all()
    steps = roadmap.steps.prefetch_related('resources').order_by('order')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_roadmap':
            roadmap.title = request.POST.get('title', roadmap.title).strip()
            roadmap.description = request.POST.get('description', '').strip()
            roadmap.topic_id = request.POST.get('topic') or None
            roadmap.is_public = request.POST.get('is_public') == 'on'
            roadmap.save()

        elif action == 'add_step':
            title = request.POST.get('step_title', '').strip()
            description = request.POST.get('step_description', '').strip()
            resource_url = request.POST.get('step_resource_url', '').strip()

            if title:
                next_order = (
                    roadmap.steps.order_by('-order')
                    .values_list('order', flat=True)
                    .first() or 0
                ) + 1

                Step.objects.create(
                    roadmap=roadmap,
                    title=title,
                    description=description,
                    order=next_order,
                    resource_url=resource_url,
                )

        elif action == 'delete_step':
            step_pk = request.POST.get('step_pk')
            Step.objects.filter(pk=step_pk, roadmap=roadmap).delete()

        elif action == 'update_step_url':
            step_pk = request.POST.get('step_pk')
            resource_url = request.POST.get('resource_url', '').strip()
            Step.objects.filter(pk=step_pk, roadmap=roadmap).update(
                resource_url=resource_url
            )

        return redirect('roadmap:edit', pk=roadmap.pk)

    return render(request, 'roadmap/edit.html', {
        'roadmap': roadmap,
        'topics': topics,
        'steps': steps,
    })

@login_required
def roadmap_delete(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk, creator=request.user)
    if request.method == 'POST':
        roadmap.delete()
        return redirect('roadmap:list')
    return render(request, 'roadmap/confirm_delete.html', {'roadmap': roadmap})


@login_required
def toggle_progress(request, step_pk):
    step = get_object_or_404(Step, pk=step_pk)
    if not step.roadmap.is_public and request.user != step.roadmap.creator:
        return redirect('roadmap:detail', pk=step.roadmap.pk)

    progress, created = UserProgress.objects.get_or_create(user=request.user, step=step)
    if not created:
        if progress.completed:
            progress.completed = False
            progress.completed_at = None
        else:
            progress.completed = True
            progress.completed_at = timezone.now()
        progress.save()
    else:

        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
    return redirect('roadmap:detail', pk=step.roadmap.pk)