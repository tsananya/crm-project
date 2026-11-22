from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.SmartLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/employees/', views.employee_list, name='employee_list'),
    path('manage/employees/add/', views.employee_form, name='employee_add'),
    path('manage/employees/<int:pk>/edit/', views.employee_form, name='employee_edit'),
    path('manage/employees/<int:pk>/toggle/', views.employee_toggle, name='employee_toggle'),
    path('m/', views.mobile_entry, name='mobile'),
    path('desktop/', views.desktop_entry, name='desktop'),
]