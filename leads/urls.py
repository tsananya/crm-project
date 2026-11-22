from django.urls import path
from . import views, staff_views

urlpatterns = [
    # admin
    path('manage/leads/', views.lead_list, name='lead_list'),
    path('manage/leads/upload/', views.lead_upload, name='lead_upload'),
    path('manage/leads/sample/', views.sample_csv, name='sample_csv'),
    path('manage/leads/assign/', views.lead_assign, name='lead_assign'),
    # staff
    path('staff/dashboard/', staff_views.staff_dashboard, name='staff_dashboard'),
    path('staff/leads/<int:pk>/', staff_views.lead_detail, name='lead_detail'),
    path('staff/leads/<int:pk>/call/', staff_views.add_call, name='add_call'),
    path('staff/leads/<int:pk>/followup/', staff_views.add_followup, name='add_followup'),
    path('staff/leads/<int:pk>/document/', staff_views.upload_document, name='upload_document'),
    path('staff/leads/<int:pk>/application/', staff_views.add_application, name='add_application'),
    path('staff/followups/', staff_views.my_followups, name='my_followups'),
    path('staff/followups/<int:pk>/done/', staff_views.followup_done, name='followup_done'),
    path('staff/performance/', staff_views.performance, name='performance'),
]