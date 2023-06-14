from django.urls import path

from .import views

urlpatterns = [
    path('SearchGov', views.SearchGov, name='API_SearchGov'),
    path('add/<str:state>/<str:pid>/', views.AddDatabase, name='API_SearchAdd'),
    path('manualadd/<str:id>/', views.ManualAdd, name='API_ManualAdd'),
    path('addMany', views.AddMany, name='API_SearchAddMany'),
    path('updateAllQld/', views.UpdateAllQLD),
    path('updateQld/', views.UpdateNewQLD), 
]
