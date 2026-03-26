from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dashboard

@login_required
def dashboard(request):
    dash, _ = Dashboard.objects.get_or_create(user=request.user)
    rank = Dashboard.objects.filter(total_score__gt=dash.total_score).count() + 1
    return render(request, 'main/dashboard.html', {'dash': dash, 'rank': rank})

@login_required
def home(request):
    return render(request, 'main/home.html')

def home_no_register(request):
    return render(request, 'main/home_.html')

