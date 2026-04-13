from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q
import uuid

from .models import Community, CommunityMembership, CommunityPost
from .decorators import community_create_required, can_create_community
from post.models import Post
from library.models import Topic
"""
Главные view функции Community:
1. community_list - Дает лист всез комюнити смотря на филтр
2. community_detail - Дает детали Community
3. community_create, community_delete - Создает Community, Удаляет Community
4. community_join, community_leave - Вход и выход в Community
5. community_post_add, community_post_remove - Добавление и удаление поста в Community
6. community_approve_member, community_reject_member - Принятие и откланение запроса в Community
"""
RESERVED_COMMUNITY_SLUGS = frozenset({
    'create', 'join', 'leave', 'delete', 'post', 'new', 'edit', 'admin', 'api',
    'approve', 'reject', 'list',
})


def community_list(request):
    q = request.GET.get('q', '').strip()
    topic_slug = request.GET.get('topic')
    communities = Community.objects.select_related('creator', 'topic').prefetch_related('memberships')
    if q:
        communities = communities.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if topic_slug:
        communities = communities.filter(topic__slug=topic_slug)
    user_community_ids = set()
    if request.user.is_authenticated:
        user_community_ids = set(
            CommunityMembership.objects
            .filter(user=request.user, is_approved=True)
            .values_list('community_id', flat=True)
        )
    topics = Topic.objects.all()
    return render(request, 'community/list.html', {
        'communities': communities,
        'user_community_ids': user_community_ids,
        'topics': topics,
        'q': q,
        'can_create': can_create_community(request.user),
    })


def community_detail(request, slug):
    community = get_object_or_404(
        Community.objects.select_related('creator', 'topic'), slug=slug
    )
    is_member = community.is_member(request.user)
    is_admin  = community.is_admin(request.user) or (
        request.user.is_authenticated and request.user == community.creator
    )
    posts = []
    if not community.is_private or is_member or is_admin:
        posts = (
            CommunityPost.objects
            .filter(community=community)
            .select_related('post__author')
            .prefetch_related('post__topics', 'post__likes', 'post__comments')
            .order_by('-pinned', '-created_at')
        )
    members = (
        CommunityMembership.objects.filter(community=community, is_approved=True).select_related('user').order_by('joined_at')[:12]
    )
    pending = []
    if is_admin:
        pending = (
            CommunityMembership.objects.filter(community=community, is_approved=False).select_related('user')
        )

    return render(request, 'community/detail.html', {
        'community': community,
        'is_member': is_member,
        'is_admin':  is_admin,
        'posts':     posts,
        'members':   members,
        'pending':   pending,
    })


@community_create_required
def community_create(request):
    topics = Topic.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        topic_id = request.POST.get('topic') or None
        is_private = request.POST.get('is_private') == 'on'

        if not name:
            return render(request, 'community/create.html', {
                'error': 'Name is required.', 'topics': topics,
            })

        base_slug = slugify(name) or 'community'
        slug = base_slug
        if slug in RESERVED_COMMUNITY_SLUGS or Community.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{uuid.uuid4().hex[:6]}'

        community = Community.objects.create(
            name=name, slug=slug, description=description,
            topic_id=topic_id, creator=request.user, is_private=is_private,
        )
        CommunityMembership.objects.create(
            community=community, user=request.user, role='admin', is_approved=True,
        )
        return redirect('community:detail', slug=community.slug)

    return render(request, 'community/create.html', {'topics': topics})


@login_required
def community_join(request, slug):
    community = get_object_or_404(Community, slug=slug)
    if request.method == 'POST':
        existing = CommunityMembership.objects.filter(community=community, user=request.user).first()
        if existing:
            if existing.is_approved:
                messages.info(request, 'You are already a member.')
            else:
                messages.info(request, 'Your request is pending approval.')
            return redirect('community:detail', slug=slug)
        is_approved = not community.is_private
        CommunityMembership.objects.create(
            community=community, user=request.user,
            role='member', is_approved=is_approved,
        )
        if is_approved:
            messages.success(request, f'You joined {community.name}!')
        else:
            messages.success(request, 'Join request sent. Waiting for approval.')
    return redirect('community:detail', slug=slug)


@login_required
def community_leave(request, slug):
    community = get_object_or_404(Community, slug=slug)
    if request.method == 'POST':
        if request.user == community.creator:
            messages.error(request, 'Creator cannot leave. Transfer ownership or delete the community.')
            return redirect('community:detail', slug=slug)
        CommunityMembership.objects.filter(community=community, user=request.user).delete()
        messages.success(request, f'You left {community.name}.')
    return redirect('community:list')


@login_required
def community_post_add(request, slug):
    community = get_object_or_404(Community, slug=slug)

    if not community.is_member(request.user) and request.user != community.creator:
        messages.error(request, 'You must be a member to post here.')
        return redirect('community:detail', slug=slug)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, pk=post_id, author=request.user)
        _, created = CommunityPost.objects.get_or_create(community=community, post=post)
        if created:
            messages.success(request, 'Post added to community.')
        else:
            messages.info(request, 'Post already in this community.')

    return redirect('community:detail', slug=slug)


@login_required
def community_post_remove(request, slug, cp_pk):
    community = get_object_or_404(Community, slug=slug)
    cp = get_object_or_404(CommunityPost, pk=cp_pk, community=community)
    is_admin = community.is_admin(request.user) or request.user == community.creator
    if request.method == 'POST':
        if cp.post.author == request.user or is_admin:
            cp.delete()
            messages.success(request, 'Post removed from community.')
        else:
            messages.error(request, 'Permission denied.')
    return redirect('community:detail', slug=slug)


@login_required
def community_approve_member(request, slug, user_pk):
    community = get_object_or_404(Community, slug=slug)
    if not (community.is_admin(request.user) or request.user == community.creator):
        return redirect('community:detail', slug=slug)
    if request.method == 'POST':
        membership = get_object_or_404(CommunityMembership, community=community, user_id=user_pk)
        membership.is_approved = True
        membership.save(update_fields=['is_approved'])
    return redirect('community:detail', slug=slug)


@login_required
def community_reject_member(request, slug, user_pk):
    community = get_object_or_404(Community, slug=slug)
    if not (community.is_admin(request.user) or request.user == community.creator):
        return redirect('community:detail', slug=slug)
    if request.method == 'POST':
        CommunityMembership.objects.filter(community=community, user_id=user_pk).delete()
    return redirect('community:detail', slug=slug)


@login_required
def community_delete(request, slug):
    community = get_object_or_404(Community, slug=slug, creator=request.user)
    if request.method == 'POST':
        community.delete()
        messages.success(request, 'Community deleted.')
        return redirect('community:list')
    return render(request, 'community/confirm_delete.html', {'community': community})