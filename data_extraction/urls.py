# Django imports.
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

# Third party imports.

# This module imports.
from . import views
from . import viewsPublic

# Other module imports.

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
    path('deleteBucket/<int:id>/',views.deleteFileBucket, name='deleteBucket'),

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

