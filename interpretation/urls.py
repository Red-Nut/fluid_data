from django.urls import path

from .import views

urlpatterns = [
    path('convert_document_pages/<int:did>/', views.ExtractTextFromDocument, name='convert_document_pages'),
    path('extract_document_data/<int:did>/<int:dataType>/', views.RunPageTextAutomation, name='extract_document_data'),
]
