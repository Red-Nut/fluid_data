from django.urls import path

from .import views

urlpatterns = [
    path('convert-document-pages/<int:did>/', views.ExtractTextFromDocumentView, name='convert_document_pages'),
    path('extract-document-data/<int:did>/<int:data_type>/', views.RunPageTextAutomationView, name='extract_document_data'),
    path('extract-document-data-method/<int:did>/<int:method_id>/', views.RunPageTextAutomationByMethodView, name='extract_document_data_method'),

    
    path('create-isotherm-template/<int:well_id>/', views.CreateIsothermTemplateView, name='create_isotherm_template'),

    path('myfun/', views.MyFun),
]
