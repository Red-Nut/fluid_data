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

from .import views

urlpatterns = [
    path('', views.index, name='admin-index'),
    path('status/', views.status, name='admin-status'),
    path('search/', views.search, name='admin-search'),
    path('operations/', views.operations, name='admin-operations'),


    path('update-companies', views.UpdateCompanies, name='admin-updateCompanies'),
    path('download-all', views.DownloadAllMissing, name='admin-DownloadAll'),
    path('download-wcr', views.DownloadAllWCRs, name='admin-DownloadWCRs'),
    path('convert', views.ConvertAllMissingToJPEG, name='admin-convertAll'),
    path('dup', views.RemoveDuplicateDocuments, name='admin-removeDuplicate'),
    path('changeWell', views.changeWell, name='admin-changeWell'),
    path('text', views.GoogleText),
]


