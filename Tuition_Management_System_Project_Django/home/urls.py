from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home-page'),
    path('login/', views.login, name='login-page'),
    path('register/', views.register, name='register-action'),
]
