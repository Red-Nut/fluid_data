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
    path('users/', views.UsersPage, name='admin-users'),
    path('wells/<int:page>/', views.WellsPage, name='admin-wells'),
    path('wells/<slug:letter>/<int:page>/', views.WellsByLetter, name='admin-wells-letter'),
    path('company/<int:id>/', views.Companies, name='admin-company'),
    path('conversion/', views.ConversionPage, name='admin-conversion'),
    path('extraction/', views.ExtractionPage, name='admin-extraction'),


    path('update-companies', views.UpdateCompanyNames, name='admin-updateCompanies'),
    path('remove-duplicate-documents', views.FixDuplicateDocumentNaming),
    

    
    path('download-all', views.DownloadAllMissing, name='admin-DownloadAll'),
    path('download-wcr', views.DownloadAllWCRs, name='admin-DownloadWCRs'),
    path('download-well/<int:id>/', views.DownloadFilesForWell),
    path('convert', views.ConvertAllMissingToJPEG, name='admin-convertAll'),
    path('convert/<int:id>/', views.ConvertToJPEG),
    path('dup', views.RemoveDuplicateDocuments, name='admin-removeDuplicate'),
    path('changeWell', views.changeWell, name='admin-changeWell'),
    path('text', views.GoogleText),
    path('myCreateUser', views.myCreateUser, name='admin-myCreateUser'),
]


