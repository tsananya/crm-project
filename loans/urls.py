from django.urls import path
from . import views

urlpatterns = [
    path('manage/banks/', views.bank_list, name='bank_list'),
    path('manage/banks/add/', views.bank_form, name='bank_add'),
    path('manage/banks/<int:pk>/edit/', views.bank_form, name='bank_edit'),
    path('manage/schemes/', views.scheme_list, name='scheme_list'),
    path('manage/schemes/add/', views.scheme_form, name='scheme_add'),
    path('manage/schemes/<int:pk>/edit/', views.scheme_form, name='scheme_edit'),
    path('manage/documents/', views.document_list, name='document_list'),
    path('manage/documents/<int:pk>/<str:action>/', views.document_verify, name='document_verify'),
    path('manage/applications/', views.application_list, name='application_list'),
    path('manage/applications/<int:pk>/update/', views.application_update, name='application_update'),
]