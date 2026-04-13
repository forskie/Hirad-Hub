from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, authenticate, logout

from django.contrib.contenttypes.models import ContentType
from post.models import Post, Favorite

from .models import CustomUser, TeacherProfile, DirectorProfile
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm, TeacherRegistrationForm, TeacherProfile
from django.contrib.auth.decorators import login_required
from user.decorators import teacher_required
from library.models import Book, Podcast, Video
from community.models import Community, CommunityMembership

"""
Представления системы пользователей.

1. аутентификация (login, logout, register)
2. выбор типа регистрации (student / teacher)
3. профиль пользователя (с рейтингом, уровнем, избранными постами)
4. просмотр профилей других пользователей (teacher/director/others)
5. редактирование профиля
6. teacher dashboard (контент преподавателя)
7. система верификации учителей (director/admin)
8. список ожидающих верификации учителей
9. расчёт уровня пользователя через score thresholds
10. интеграция с постами, библиотекой и сообществами
"""

def register(request):
    return redirect('user:register_choice')


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user:profile')
    else:   
        form = CustomUserLoginForm()
    return render(request, 'user/register/login.html', {'form' : form})


def profile_view_others(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    if other_user.role == 'teacher':
        try:
            profile = other_user.teacher_profile
        except TeacherProfile.DoesNotExist:
            profile = None
        books    = Book.objects.filter(creator=other_user).order_by('-created_at')
        videos   = Video.objects.filter(creator=other_user).order_by('-created_at')
        podcasts = Podcast.objects.filter(creator=other_user).order_by('-created_at')
        return render(request, 'user/profile/teacher_profile.html', {
            'teacher':  other_user,
            'profile':  profile,
            'books':    books,
            'videos':   videos,
            'podcasts': podcasts,
        })

    director_profile = None
    if other_user.role == 'director':
        try:
            director_profile = other_user.director_profile
        except DirectorProfile.DoesNotExist:
            director_profile = None

    return render(request, 'user/profile/others_profile.html', {
        'profile_user': other_user,
        'director_profile': director_profile,
    })


LEVEL_THRESHOLDS = [0, 1000, 5000, 10000, 20000, 35000, 45000, 55000, 70000, 100000]
 
@login_required
def profile_view(request):
    user = request.user
    communities = []
    pending_teachers = []
    pending_count = 0

    if user.role == 'director':
        communities = (
            Community.objects
            .filter(
                memberships__user=user,
                memberships__role='admin',
                memberships__is_approved=True,
            )
            .select_related('creator', 'topic')
            .distinct()
            .order_by('-created_at')
        )
        pending_qs = TeacherProfile.objects.filter(
            is_verified=False, user__role='teacher'
        ).select_related('user', 'school')
        try:
            director_school = user.director_profile.school
            if director_school:
                pending_qs = pending_qs.filter(school=director_school)
            else:
                pending_qs = pending_qs.none()
        except Exception:
            pass
        pending_teachers = pending_qs
        pending_count = pending_qs.count()

    from post.models import Post, Favorite
    from django.contrib.contenttypes.models import ContentType

    post_ct = ContentType.objects.get_for_model(Post)
    favorite_posts = Post.objects.filter(
        id__in=Favorite.objects.filter(
            user=user, content_type=post_ct
        ).values_list('object_id', flat=True)
    ).select_related('author').prefetch_related('likes', 'comments')
 
    level_idx = min(user.level - 1, len(LEVEL_THRESHOLDS) - 1)
    level_current_min = LEVEL_THRESHOLDS[level_idx]
    if user.level < 10:
        level_next_min = LEVEL_THRESHOLDS[min(level_idx + 1, len(LEVEL_THRESHOLDS) - 1)]
        score_in_level = user.score - level_current_min
        level_range    = level_next_min - level_current_min
        level_progress_pct = min(int(score_in_level / level_range * 100), 100) if level_range > 0 else 100
    else:
        level_current_min  = LEVEL_THRESHOLDS[-1]
        level_next_min     = level_current_min
        level_progress_pct = 100
 
    teacher_profile  = None
    director_profile = None
    teacher_books    = []
    teacher_videos   = []
    teacher_podcasts = []
 
    if user.role in ('teacher', 'director', 'admin'):
        from library.models import Book, Video, Podcast
        try:
            teacher_profile = user.teacher_profile
        except Exception:
            pass
 
        teacher_books    = Book.objects.filter(creator=user).order_by('-created_at')
        teacher_videos   = Video.objects.filter(creator=user).order_by('-created_at')
        teacher_podcasts = Podcast.objects.filter(creator=user).order_by('-created_at')
 
        if user.role == 'director':
            try:
                director_profile = user.director_profile
            except Exception:
                pass
 
    return render(request, 'user/profile/profile.html', {
        'user':              user,
        'favorite_posts':    favorite_posts,
        'level_current_min': level_current_min,
        'level_next_min':    level_next_min,
        'level_progress_pct': level_progress_pct,
        'teacher_profile':   teacher_profile,
        'director_profile':  director_profile,
        'teacher_books':     teacher_books,
        'teacher_videos':    teacher_videos,
        'teacher_podcasts':  teacher_podcasts,
        'communities':      communities,
        'pending_teachers': pending_teachers,
        'pending_count':    pending_count,
    })
 

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if request.FILES.get('profile_picture'):
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            form.save_m2m()
            return redirect('user:profile')
        else:
            print(form.errors)
    else:
        form = CustomUserUpdateForm(instance=user)
    return render(request, 'user/profile/edit_profile.html', {'form': form, 'user': user})


def logout_view(request):
    logout(request)
    return redirect('main:home')


def register_choice(request):
    return render(request, 'user/register/register_choice.html')


def register_student(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if  form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register/register_student.html', {'form' : form})
        

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user:pending_verification')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'user/register/register_teacher.html', {'form' : form})


def pending_verification(request):
    return render(request, 'user/pending_verification.html')


def teacher_profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username, role='teacher')
    try:
        profile = user.teacher_profile
    except TeacherProfile.DoesNotExist:
        profile = None

    books   = Book.objects.filter(creator=user).order_by('-created_at')
    videos  = Video.objects.filter(creator=user).order_by('-created_at')
    podcasts = Podcast.objects.filter(creator=user).order_by('-created_at')

    return render(request, 'user/profile/teacher_profile.html', {
        'teacher':  user,
        'profile':  profile,
        'books':    books,
        'videos':   videos,
        'podcasts': podcasts,
    })


@login_required
def teacher_dashboard(request):
    if request.user.role not in ['teacher', 'admin', 'director']:
        return redirect('main:home')

    try:
        profile = request.user.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('main:home')

    books = Book.objects.filter(creator=request.user).order_by('-created_at')
    videos = Video.objects.filter(creator=request.user).order_by('-created_at')
    podcasts = Podcast.objects.filter(creator=request.user).order_by('-created_at')

    return render(request, 'user/teacher_dashboard.html', {
        'profile': profile,
        'books':   books,
        'videos':  videos,
        'podcasts': podcasts,
    })


@login_required
def verify_teacher(request, username):
    from django.contrib import messages

    if request.user.role not in ['director', 'admin']:
        return redirect('main:home')

    teacher = get_object_or_404(CustomUser, username=username)
    if teacher.role != 'teacher':
        messages.error(request, 'This action applies to teacher accounts only.')
        return redirect('user:pending_teachers')

    try:
        profile = teacher.teacher_profile
    except TeacherProfile.DoesNotExist:
        return redirect('main:home')

    if request.user.role == 'director':
        try:
            director_school = request.user.director_profile.school
        except DirectorProfile.DoesNotExist:
            director_school = None

        if not director_school or profile.school_id != director_school.id:
            messages.error(request, 'You can verify only teachers from your school.')
            return redirect('user:pending_teachers')

    if request.method == 'POST':
        from django.utils import timezone
        profile.is_verified   = True
        profile.verified_at   = timezone.now()
        profile.verified_by   = request.user
        profile.save(update_fields=['is_verified', 'verified_at', 'verified_by'])
        if request.user.role == 'director':
            try:
                dir_profile = request.user.director_profile
                dir_profile.teachers_verified += 1
                dir_profile.save(update_fields=['teachers_verified'])
            except DirectorProfile.DoesNotExist:
                pass

        return redirect('user:teacher_profile', username=username)

    return render(request, 'user/verify_teacher.html', {
        'teacher': teacher,
        'profile': profile,
    })


@login_required
def pending_teachers(request):
    if request.user.role not in ['director', 'admin']:
        return redirect('main:home')

    teachers = TeacherProfile.objects.filter(
        is_verified=False, user__role='teacher'
    ).select_related('user', 'school').order_by('created_at')

    if request.user.role == 'director':
        try:
            director_school = request.user.director_profile.school
            if director_school:
                teachers = teachers.filter(school=director_school)
            else:
                teachers = teachers.none()
        except DirectorProfile.DoesNotExist:
            teachers = teachers.none()

    return render(request, 'user/pending_teachers.html', {'teachers': teachers})