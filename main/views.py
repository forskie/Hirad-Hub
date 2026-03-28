from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dashboard

@login_required
def dashboard(request):
    dash, _ = Dashboard.objects.get_or_create(user=request.user)
    rank = Dashboard.objects.filter(total_score__gt=dash.total_score).count() + 1
    return render(request, 'main/dashboard.html', {'dash': dash, 'rank': rank})


def home(request):
    return render(request, 'main/home.html')

def search(request):
    query = request.GET.get('q', '')
    return render(request, 'main/search.html', {'query': query})

def leaderboard(request):
    leaders = Dashboard.objects.order_by('-total_score')[:10]
    return render(request, 'main/leaderboard.html', {'leaders': leaders})