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
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Built-in.
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # PAGES WHEN LOGGED OUT.
    path('', viewsPublic.index, name='index'),
    path('about', viewsPublic.about, name='about'),
    path('pricing', viewsPublic.pricing, name='pricing'),
    path('contact', viewsPublic.contact, name='contact'),

    # PAGES WHEN LOGGED IN.
    path('home', views.index, name='home'),

        # Searching
    path('search', views.search, name='search'),
    path('las_files', views.lasFiles, name='las'),
    path('file_bucket', views.fileBucketNone, name='fileBucket'),
    path('file_bucket/<int:id>/', views.fileBucketID, name='fileBucketID'),
    path('saveToFileBucket',views.saveToFileBucket, name='saveToFileBucket'),
    path('emptyBucket',views.emptyFileBucketRequest, name='emptyBucket'),
    path('saveBucket',views.saveFileBucket, name='saveBucket'),

        # API Page.
    path('api_page', views.api, name='api'),

        # Profile Pages.
    path('profile', views.profile, name='profile'),
    path('company', views.company, name='company'),

        # Well Details Page
    path('well/<int:id>/', views.details, name='details'),

        # Logout
    path('logout', views.logout_view, name='logout'),

    # INCLUDES
    # admin
    path('administration/', include('administration.urls')),

    # Search
    path('searchGov/', include('search.urls')),

    # API
    path('api/', include('api.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

