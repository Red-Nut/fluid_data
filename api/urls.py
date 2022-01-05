# Django imports.
from django.urls import path

# Third party imports.

# This module imports.
from .import externalAPI, vA

# Other module imports.

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
