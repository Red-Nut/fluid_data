from django.urls import path

from .import views

urlpatterns = [
    path('convert_document_pages/<int:did>/', views.ExtractTextFromDocumentView, name='convert_document_pages'),
    path('extract_document_data/<int:did>/<int:data_type>/', views.RunPageTextAutomationView, name='extract_document_data'),
]
