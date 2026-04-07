from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, authenticate, logout

from django.contrib.contenttypes.models import ContentType
from post.models import Post, Favorite

from .models import CustomUser, TeacherProfile
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm, TeacherRegistrationForm
from django.contrib.auth.decorators import login_required


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
    return render(request, 'user/login.html', {'form' : form})


def profile_view_others(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    return render(request, 'user/others_profile.html', {'user' : other_user})


@login_required
def profile_view(request):
    user = request.user
    post_ct = ContentType.objects.get_for_model(Post)
    favorite_posts = Post.objects.filter(
        id__in=Favorite.objects.filter(
            user=user,
            content_type=post_ct
        ).values_list('object_id', flat=True)
    ).select_related('author').prefetch_related('likes', 'comments')
    return render(request, 'user/profile.html', {
        'user': user,
        'favorite_posts': favorite_posts
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
    return render(request, 'user/edit_profile.html', {'form': form, 'user': user})


def logout_view(request):
    logout(request)
    return redirect('main:home')


def register_choice(request):
    return render(request, 'user/register_choice.html')

def register_student(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if  form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register_student.html', {'form' : form})
        

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user:pending_verification')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'user/register_teacher.html', {'form' : form})


def pending_verification(request):
    return render(request, 'user/pending_verification.html')

        