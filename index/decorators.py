from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from .models import Пользователь

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.session.get('user_id'):
                return redirect('login')
            try:
                user_custom = Пользователь.objects.get(id=request.session['user_id'])
                if user_custom.Роль == role:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("Доступ запрещён")
            except Пользователь.DoesNotExist:
                return HttpResponseForbidden("Пользователь не найден")
        return _wrapped_view
    return decorator

def custom_user_required(view_func):
    """Декоратор для кастомных пользователей"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def planning_required(view_func):
    """Декоратор для специалистов по планированию"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        try:
            user_custom = Пользователь.objects.get(id=request.session['user_id'])
            if user_custom.Отдел and user_custom.Отдел.Название == 'Отдел по планированию и анализу':
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Доступ разрешен только для отдела планирования и анализа")
        except Пользователь.DoesNotExist:
            return HttpResponseForbidden("Пользователь не найден")
    return _wrapped_view