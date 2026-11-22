from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('manage/employees/', views.employee_list, name='employee_list'),
    path('manage/employees/add/', views.employee_form, name='employee_add'),
    path('manage/employees/<int:pk>/edit/', views.employee_form, name='employee_edit'),
    path('manage/employees/<int:pk>/toggle/', views.employee_toggle, name='employee_toggle'),
]