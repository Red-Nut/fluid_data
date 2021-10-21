"""data_extraction URL Configuration

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
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from . import views
from . import viewsPublic

urlpatterns = [
    # Built-in Admin Tool.
    path('admin/', admin.site.urls),

    # Pages When Not Logged In.
    path('', viewsPublic.index, name='index'),
    path('about', viewsPublic.about, name='about'),
    path('pricing', viewsPublic.pricing, name='pricing'),
    path('contact', viewsPublic.contact, name='contact'),

    # Pages When Logged In.
    path('home', views.index, name='home'),
    path('search', views.search, name='search'),
    path('api', views.api, name='api'),
    path('profile', views.profile, name='profile'),
    path('company', views.company, name='company'),
    path('well/<int:id>/', views.details, name='details'),

    # admin
    path('administration/', include('administration.urls')),

    # Search
    path('searchGov/', include('search.urls')),

    # API
    path('api/', include('api.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

