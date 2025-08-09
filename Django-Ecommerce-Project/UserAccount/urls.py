"""Furniture_Ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from UserAccount import views as user_views


urlpatterns = [
    path('login', user_views.LoginView.as_view(), name="login"),
    path('register', user_views.RegistrationView.as_view(), name="register"),
    path('Logout', user_views.Logout, name="Logout"),
    path('UserAccount', user_views.UserAccountView.as_view(), name="UserAccount"),
]
