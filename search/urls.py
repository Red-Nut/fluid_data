from django.urls import path

from .import views

urlpatterns = [
    path('SearchGov', views.SearchGov, name='API_SearchGov'),
    path('add', views.AddDatabase, name='API_SearchAdd'),
    path('addMany', views.AddMany, name='API_SearchAddMany'),
]
