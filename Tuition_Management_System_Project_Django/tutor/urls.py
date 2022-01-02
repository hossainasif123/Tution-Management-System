from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='tutor-home'),
    path('feed/', views.feed, name='tutor-feed'),
    path('apply/<int:ad_id>/', views.apply, name='tutor-apply'),
    path('feedback/<int:ad_id>/', views.feedback, name='tutor-feedback'),
    path('profile/<int:profile_id>/', views.view_profile, name='tutor-profile'),
    path('profile/<int:profile_id>/edit', views.edit_profile, name='tutor-edit-profile'),
    path('history/', views.history, name='tutor-history'),
    path('settings/', views.settings, name='tutor-settings'),
    path('logout/', views.logout, name='tutor-logout'),
    path('login/', views.login, name='tutor-login'),
]
