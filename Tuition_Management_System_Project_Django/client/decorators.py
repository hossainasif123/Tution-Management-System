from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def client_required(function):
    def wrapper(request, *args, **kwargs):
        decorated_view_func = login_required(request)
        if not decorated_view_func.user.is_authenticated:
            messages.warning(request, 'Please login first')
            return redirect('login-page')

        if not request.user.is_client:
            return redirect('home-page')
        else:
            return function(request, *args, **kwargs)

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper
