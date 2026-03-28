from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'user/register_success.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})

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

def profile_view_others(request):
    other_user = get_object_or_404(CustomUser, username=username)
    return render(request, 'user/others_profile.html', {'user' : other_user})


@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'user/edit_profile.html', {'user': request.user, 'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

