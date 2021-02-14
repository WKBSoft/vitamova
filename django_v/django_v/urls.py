"""django_v URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from . import authentication

urlpatterns = [
    path("login/",authentication.login,name='login'),
    path("signup/",authentication.signup,name="signup"),
    path("logout/",authentication.logout,name="logout"),
    path("account/",authentication.account,name="account"),
    path("",views.home,name='home'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("read/", views.read, name='read'),
    path("flashcards/",views.flashcards,name="flashcards"),
    #path("transcribe/",views.transcribe,name="transcribe"),
    #path("accent/",views.accent,name="accent"),
    path("typing/",views.typing,name="typing"),
]
