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
from Products import views as prod_views


urlpatterns = [
    path('<str:search>/<str:id>/<str:pg_num>', prod_views.ViewProducts.as_view(), name="product-list"),
    path('<int:id>', prod_views.ProductDetailView.as_view(), name="product"),
    path('submit_review/<str:id>', prod_views.ReviewFormView.as_view(), name="submit_review"),
]