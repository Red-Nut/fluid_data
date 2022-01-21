# Django imports.
from django.urls import path

# Third party imports.

# This module imports.
from .import vA, vB, vC

# Other module imports.
from data_extraction import views


urlpatterns = [
    # Internal API

    # Current Stable External API
    path('', views.api),
    path('wellList/', vC.wellList),
    path('wellListID/', vC.wellListID),
    path('wellSearch/', vC.search),
    path('well/<int:id>', vC.retrieveId),
    path('well/<str:name>', vC.retrieveName),
    
    # Version A
    path('vA/wellList/', vA.wellList),
    path('vA/wellListID/', vA.wellListID),
    path('vA/wellSearch/', vA.search),
    path('vA/well/<int:id>', vA.retrieveId),
    path('vA/well/<str:name>', vA.retrieveName),

    # Version B
    path('vB/wellList/', vB.wellList),
    path('vB/wellListID/', vB.wellListID),
    path('vB/wellSearch/', vB.search),
    path('vB/well/<int:id>', vB.retrieveId),
    path('vB/well/<str:name>', vB.retrieveName),

    # Version C
    path('vC/wellList/', vC.wellList),
    path('vC/wellListID/', vC.wellListID),
    path('vC/wellSearch/', vC.search),
    path('vC/well/<int:id>', vC.retrieveId),
    path('vC/well/<str:name>', vC.retrieveName),
    
]
