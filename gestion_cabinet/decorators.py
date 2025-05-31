from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied

def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'patient'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès réservé aux patients.")
        return redirect('home')
    return _wrapped_view

def dentiste_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'dentiste'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès réservé aux dentistes.")
        return redirect('home')
    return _wrapped_view

def secretaire_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'secretaire'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès réservé aux secrétaires.")
        return redirect('home')
    return _wrapped_view

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            has_permission = False
            if 'PATIENT' in allowed_roles and hasattr(request.user, 'patient'):
                has_permission = True
            elif 'DENTISTE' in allowed_roles and hasattr(request.user, 'dentiste'):
                has_permission = True
            elif 'SECRETAIRE' in allowed_roles and hasattr(request.user, 'secretaire'):
                has_permission = True
            
            if has_permission:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
            return redirect('home')
        return _wrapped_view
    return decorator 