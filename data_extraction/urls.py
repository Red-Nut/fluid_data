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
from .settings import base

from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('well/<int:id>/', views.details, name='details'),

    # admin
    #path('administration/', views.administration, name='administration'),
    path('administration/search/', views.search, name='search'),
    path('administration/update-companies', views.UpdateCompanies),
    path('administration/download-files', views.DownloadMissingFiles),
    
    # Search
    path('searchGov/', include('search.urls')),

    # API
    path('api/', include('api.urls')),
]

urlpatterns += static(base.STATIC_URL, document_root = base.STATIC_ROOT)
urlpatterns += static(base.MEDIA_URL, document_root=base.MEDIA_ROOT)

