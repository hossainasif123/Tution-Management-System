from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import User
from django.urls import reverse


def home(request):
    return render(request, 'home/home.html')


def login(request):
    current_tab = request.GET.get('tab', 'client')
    email = request.GET.get('email', '')
    context = {
        'logged_in': False,
        'is_client': False,
        'is_tutor': False,
        'email': email,
        'current_tab': current_tab,
        'tutor_tab': 'show' if current_tab == 'tutor' else '',
        'client_tab': 'show' if current_tab == 'client' else '',
    }
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.pk)
        context['logged_in'] = True
        context['is_client'] = user.is_client
        context['is_tutor'] = user.is_tutor
        return render(request, 'home/login.html', context=context)
    else:
        return render(request, 'home/login.html', context=context)


def register(request):
    user_type = request.POST['user_type']
    full_name = request.POST['full_name']
    email = request.POST['email']
    password = request.POST['password']
    user = User.objects.filter(email=email)
    if user_type == 'client':
        if not user.exists():
            user = User.objects.create_user(full_name, email, 'client', password)
            if user is None:
                messages.error(request, 'Cannot create account, try again later')
            else:
                messages.success(request, 'Account is successfully created. Welcome!')
                return redirect('client-home')
        else:
            user = user[0]
            if not user.is_client:
                user.is_client = True
                user.save()
                messages.success(request, 'You\'re successfully added as a client.')
                return redirect('client-home')
            else:
                messages.error(request, 'Account already exists, try with a different email.')
                return redirect('{}#signup_client'.format(reverse('home-page')))
    elif user_type == 'tutor':
        if not user.exists():
            user = User.objects.create_user(full_name, email, 'tutor', password)
            if user is None:
                messages.error(request, 'Cannot create account, try again later')
            else:
                messages.success(request, 'Account is successfully created. Welcome!')
                return redirect('tutor-home')
        else:
            user = user[0]
            if not user.is_tutor:
                user.is_tutor = True
                user.save()
                messages.success(request, 'You\'re successfully added as a tutor.')
                return redirect('tutor-home')
            else:
                messages.error(request, 'Account already exists, try with a different email.')
                return redirect('{}#signup_tutor'.format(reverse('home-page')))
    else:
        messages.error(request, 'Invalid user type.')

    return redirect('home-page')
