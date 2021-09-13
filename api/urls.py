from django.urls import path

from .import internalAPI, externalAPI, vA

urlpatterns = [
    # Internal API

    # External API
    path('', externalAPI.index),
    
    # Version A
    path('vA/wellList/', vA.wellList),
    path('vA/wellListID/', vA.wellListID),
    path('vA/wellSearch/', vA.search),
    path('vA/well/<int:id>', vA.retrieveId),
    path('vA/well/<str:name>', vA.retrieveName),
    
]
