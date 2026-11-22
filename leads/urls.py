from django.urls import path
from . import views

urlpatterns = [
    path('manage/leads/', views.lead_list, name='lead_list'),
    path('manage/leads/upload/', views.lead_upload, name='lead_upload'),
    path('manage/leads/sample/', views.sample_csv, name='sample_csv'),
    path('manage/leads/assign/', views.lead_assign, name='lead_assign'),
]