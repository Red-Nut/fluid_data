# Django imports.
from django.urls import path

# Third party imports.

# This module imports.
from .import vA, vB

# Other module imports.
from data_extraction import views


urlpatterns = [
    # Internal API

    # External API
    path('', views.api),
    path('wellList/', vB.wellList),
    path('wellListID/', vB.wellListID),
    path('wellSearch/', vB.search),
    path('well/<int:id>', vB.retrieveId),
    path('well/<str:name>', vB.retrieveName),
    
    # Version A
    path('vA/wellList/', vA.wellList),
    path('vA/wellListID/', vA.wellListID),
    path('vA/wellSearch/', vA.search),
    path('vA/well/<int:id>', vA.retrieveId),
    path('vA/well/<str:name>', vA.retrieveName),

    # Version A
    path('vB/wellList/', vB.wellList),
    path('vB/wellListID/', vB.wellListID),
    path('vB/wellSearch/', vB.search),
    path('vB/well/<int:id>', vB.retrieveId),
    path('vB/well/<str:name>', vB.retrieveName),
    
]
