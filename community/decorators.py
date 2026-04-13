from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from gamification.constants import LEVELS, TEACHER_LEVELS


def _student_min_level(score):
    """Через оценок возврашает уроыен студента """
    level = 1
    for min_score, lvl_num, _ in LEVELS:
        if score >= min_score:
            level = lvl_num
    return level


def _teacher_min_level(teacher_score):
    level = 1
    for min_score, lvl_num, _ in TEACHER_LEVELS:
        if teacher_score >= min_score:
            level = lvl_num
    return level


def community_create_required(view_func):
    """
    Чекает может ли юзер создать Community (для учителей с 3 уровня, ученики с 5)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('user:login')
        if user.role in ('director', 'admin'):
            return view_func(request, *args, **kwargs)
        if user.role == 'teacher':
            try:
                tp = user.teacher_profile
                if _teacher_min_level(tp.teacher_score) >= 3:
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass
            messages.error(request, 'You need Teacher level 3 (Adept) to create a community.')
            return redirect('community:list')
        if _student_min_level(user.score) >= 5:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You need level 5 (Researcher) to create a community.')
        return redirect('community:list')
    return wrapper


def can_create_community(user):
    """
    Проверяет не админ или директор ли юзер
    """
    if not user.is_authenticated:
        return False
    if user.role in ('director', 'admin'):
        return True
    if user.role == 'teacher':
        try:
            return _teacher_min_level(user.teacher_profile.teacher_score) >= 3
        except Exception:
            return False
    return _student_min_level(user.score) >= 5