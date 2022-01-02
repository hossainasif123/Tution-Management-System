from django.contrib.auth import (
    authenticate,
    login as login_user,
    logout as logout_user
)
from users.models import User, Phone, Verification
from tuition.models import Ad, Assignee, Proposal, Question
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .decorators import client_required
from time import time
import datetime
import os
from .models import ClientFeedback
from tutor.models import TutorFeedback


@client_required
def home(request):
    """Show only the ads posted by the client which are not timed out and not already taken"""
    return render(request, 'client/feed.html', context={
        'feed_list': get_feed_list(
            request,
            Ad.objects.filter(timeout__gte=timezone.now(), client=request.user, taken=False).order_by('-ad_time')
        ),
        'display_url': True,
        'client_home': 'active',
        'show_applicant_number': True,
    })


@client_required
def view_ad(request, ad_id):
    ad = Ad.objects.filter(pk=ad_id, client=request.user)
    if ad.exists():
        ad = ad[0]
        if ad.taken:
            proposals = False
            assignee = Assignee.objects.get(ad=ad)
            c_feedback = ClientFeedback.objects.filter(ad=ad)
            c_feedback = c_feedback[0] if c_feedback.exists() else False
            t_feedback = TutorFeedback.objects.filter(ad=ad)
            t_feedback = t_feedback[0] if t_feedback.exists() else False
            _running = assignee.to_date is None or assignee.to_date > timezone.now().date()
        else:
            proposals = Proposal.objects.filter(ad=ad_id)
            proposals = proposals if proposals.exists() else False
            assignee = False
            c_feedback = False
            t_feedback = False
            _running = False
        return render(request, 'client/view_ad.html', context={
            'feed': get_feed(request, ad),
            'proposals': proposals,
            'assignee': assignee,
            'c_feedback': c_feedback,
            't_feedback': t_feedback,
            'running': _running,
        })
    else:
        return redirect('client-home')


@client_required
def feedback(request, ad_id):
    ad = Ad.objects.filter(pk=ad_id, taken=True, client=request.user)
    if not ad.exists():
        return redirect('client-home')
    ad = ad[0]
    if request.POST:
        allowed_rating = [1, 2, 3, 4, 5]
        rating = int(request.POST.get('rating', ''))
        _feedback = request.POST.get('feedback', '')
        if rating not in allowed_rating:
            messages.error(request, 'Invalid rating.')
            return render(request, 'client/feedback.html', context={
                'feed': get_feed(request, ad),
                'feedback': _feedback,
            })
        if not ClientFeedback.objects.filter(ad=ad).exists():
            ClientFeedback.objects.create(ad=ad, rating=rating, feedback=_feedback)
        messages.success(request, 'Feedback added.')
        return redirect('client-applicants', ad.pk)
    else:
        return render(request, 'client/feedback.html', context={
            'feed': get_feed(request, ad),
        })


@client_required
def accept(request, ad_id, user_id):
    ad = Ad.objects.get(pk=ad_id, client=request.user)
    ad.taken = True
    Assignee.objects.create(ad=ad, tutor_id=user_id, from_date=timezone.now())
    ad.save()
    messages.success(request, 'Proposal is accepted successfully.')
    return redirect('client-applicants', ad.pk)


@client_required
def terminate(request, ad_id):
    ad = Assignee.objects.get(ad_id=ad_id, ad__client=request.user)
    ad.to_date = timezone.now()
    ad.save()
    messages.success(request, 'The tuition is terminated successfully!')
    return redirect('client-applicants', ad.pk)


@client_required
def new(request):
    if request.POST:
        std_genders = {
            'male': 'Male',
            'female': 'Female',
            'mixed': 'Mixed',
        }
        pref_genders = {
            'male': 'Male',
            'female': 'Female',
            'any': 'Any',
        }
        title = request.POST.get('title', False)
        description = request.POST.get('description', False)
        questions = request.POST.get('questions', False)
        subjects = request.POST.get('subjects', False)
        _type = request.POST.get('type', False)
        grade = request.POST.get('grade', False)
        gender = request.POST.get('gender', False)
        std_count = request.POST.get('std_count', False)
        pref_gender = request.POST.get('pref_gender', False)
        _time = request.POST.get('time', False)
        days = request.POST.get('days', False)
        location = request.POST.get('location', False)
        salary = request.POST.get('salary', False)
        timeout = request.POST.get('timeout', False)  # date FIXME: the date format may be wrong
        try:
            t_timeout = datetime.datetime.strptime(timeout, "%d/%m/%Y").date()
        except ValueError:
            t_timeout = False

        if title and description and subjects and _type and grade and std_genders.get(gender, False) and std_count and\
                pref_genders.get(pref_gender, False) and _time and days and location and salary and t_timeout:
            ad = Ad.objects.create(title=title, description=description, subjects=subjects, type=_type, grade=grade,
                                   gender=std_genders.get(gender, False), std_count=int(std_count),
                                   pref_gender=pref_genders.get(pref_gender, False), time=_time,
                                   days=int(days), location=location, salary=int(salary), client=request.user,
                                   timeout=t_timeout)
            if ad is not None:
                if questions:
                    questions = questions.split('\n')
                    for question in questions:
                        Question.objects.create(ad=ad, question=question)
                messages.success(request, 'Ad is successfully created!')
                return redirect('client-applicants', ad.pk)

        messages.error(request, 'Please fill out all the fields.')
        return render(request, 'client/new_ad.html', context={
            'title': title,
            'description': description,
            'subjects': subjects,
            'type': _type,
            'grade': grade,
            'gender': gender,
            'std_count': std_count,
            'pref_gender': pref_gender,
            'time': _time,
            'days': days,
            'location': location,
            'salary': salary,
            'timout': timeout,
        })
    else:
        return render(request, 'client/new_ad.html')


@client_required
def view_profile(request, profile_id):
    """View only tutor profile"""
    user = User.objects.filter(pk=profile_id, is_tutor=True)
    if user.exists():
        user = user[0]
        work_history = Assignee.objects.filter(tutor=user, to_date__lte=timezone.now())
        return render(request, 'client/view_profile.html', context={
            'profile': user,
            'education': user.education_set.all().order_by('-to_year'),
            'work_history': work_history,
            'profile_img': os.path.basename(user.profile_img),
        })
    else:
        redirect('client-home')


@client_required
def history(request):
    archived_list = []
    archived_jobs = Assignee.objects.filter(to_date__lte=timezone.now(), ad__client=request.user)
    for obj in archived_jobs:
        archived_list.append(obj.ad)
    timed_out_ads = Ad.objects.filter(timeout__lte=timezone.now(), taken=False, client=request.user)
    for obj in timed_out_ads:
        archived_list.append(obj)
    return render(request, 'client/history.html', context={
        'feed_archive': get_feed_list(request, archived_list),
        'client_history': 'active',
        'show_feedback': True,
        'display_url': True,
        'show_assignee': True,
        'whos_feedback': 'Your',
    })


@client_required
def running(request):
    """Show ads that are assigned by the client"""
    active_list = []
    active_jobs = Assignee.objects.filter(to_date__gt=timezone.now(), ad__client=request.user)
    for obj in active_jobs:
        active_list.append(obj.ad)
    active_jobs = Assignee.objects.filter(to_date__isnull=True, ad__client=request.user)
    for obj in active_jobs:
        active_list.append(obj.ad)
    return render(request, 'client/running.html', context={
        'feed_list': get_feed_list(request, active_list),
        'client_running': 'active',
        'show_end_job': True,
        'show_assignee': True,
        'display_url': True,
    })


@client_required
def settings(request):
    if request.POST:
        name = request.POST.get('full_name', '')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        gender = request.POST.get('gender', '')
        email1 = request.POST.get('email1', '')
        email2 = request.POST.get('email2', '')
        phone = request.POST.get('phone', '')
        old_pass = request.POST.get('old_password', '')
        pass1 = request.POST.get('password1', '')
        pass2 = request.POST.get('password2', '')
        doc_type = request.POST.get('document_type', '')
        user = User.objects.get(pk=request.user.pk)
        # Change name
        if name != '':
            user.name = name
        # Change bio
        if bio != '':
            user.bio = bio
        # Change location
        if location != '':
            user.location = location
        # Change gender
        if gender != '':
            if gender == 'male':
                user.gender = 'Male'
            elif gender == 'female':
                user.gender = 'Female'
        # Change password
        if old_pass != '':
            chk_user = authenticate(email=user.email, password=old_pass, is_active=True)
            if chk_user is not None:
                if pass1 == pass2 and pass1 != '':
                    user.set_password(pass1)
                else:
                    messages.error(request, 'Passwords do not match!')
                    return redirect(request.path_info)
            else:
                messages.error(request, 'Wrong password. Please try again.')
                return redirect(request.path_info)
        # Add email
        if email1 != '' and email1 == email2:
            if User.objects.filter(email=email1).exists():
                messages.error(request, 'Email already exists, please try with a new one.')
                return redirect(request.path_info)
            user.email = email1
        # Add phone
        if phone != '':
            if user.phone_set.exists():
                user.phone_set.update(phone_no=phone)
            else:
                user.phone_set.create(phone_no=phone)
        # Add verification info
        if request.FILES.get('verification_document', False) and doc_type != '':
            if user.verification_set.count():
                messages.error(request, 'Required file for verification is already uploaded.')
                return redirect(request.path_info)
            file_name = handle_verification_file(request.FILES['verification_document'])
            user.verification_set.create(type=doc_type, file=file_name)
        # Upload user photo
        if request.FILES.get('profile_img'):
            file_name = handle_profile_image(request.FILES['profile_img'])
            user.profile_img = file_name
        user.save()
        messages.success(request, 'Changes are saved successfully.')
        return redirect(request.path_info)
    else:
        user = User.objects.get(pk=request.user.pk)
        phone = Phone.objects.filter(user=user)
        verification = Verification.objects.filter(user=user)
        return render(request, 'client/settings.html', context={
            'verification': verification[0] if verification.exists() else False,
            'client_settings': 'active',
            'user': user,
            'phone': phone[0].phone_no if phone.exists() else False,
        })


@client_required
def logout(request):
    logout_user(request)
    messages.info(request, 'You\'ve been successfully logged out!')
    return redirect('home-page')


def login(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, email=email, password=password, is_active=True)
    if user is not None:
        if user.is_client:
            login_user(request, user)
            return redirect('client-home')
        else:
            messages.error(request, 'Client not found, are you a tutor?')
            return redirect('{}?tab=client&email={}'.format(reverse('login-page'), email))
    else:
        messages.error(request, 'Invalid email or password! Please enter the right user credentials to login.')
        return redirect('{}?tab=client&email={}'.format(reverse('login-page'), email))


# Helper functions #


def get_feed(request, ad):
    _feedback = ClientFeedback.objects.filter(ad=ad)
    return {
        'ad': ad,
        'pk': ad.pk,
        'title': ad.title,
        'description': ad.description,
        'grade': ad.grade,
        'type': ad.type,
        'subjects': ad.subjects,
        'salary': ad.salary,
        'gender': ad.gender,
        'std_count': ad.std_count,
        'days': ad.days,
        'time': ad.time,
        'location': ad.location,
        'client': ad.client,
        'proposals': ad.proposal_set.count(),
        'feedback': _feedback[0] if _feedback.exists() else False,
    }


def get_feed_list(request, ads):
    ad_list = []
    for ad in ads:
        ad_list.append(get_feed(request, ad))
    return ad_list


def handle_verification_file(f):
    file_name = 'file_{}_{}'.format(int(time()), f.name)
    with open('/Volumes/Fallout/v_files/{}'.format(file_name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name


def handle_profile_image(f):
    file_name = 'file_{}_{}'.format(int(time()), f.name)
    with open('/Volumes/Fallout/Projects/TuitionManagament/TuitionMGMT/TuitionManagement/users/static/profile_imgs/{}'.format(file_name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name
