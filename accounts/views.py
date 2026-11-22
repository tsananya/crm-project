from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import admin_required, staff_required


@login_required
def home(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('staff_dashboard')


def logout_view(request):
    logout(request)
    return redirect('login')


@admin_required
def admin_dashboard(request):
    return render(request, 'admin_portal/dashboard.html')


@staff_required
def staff_dashboard(request):
    return render(request, 'staff_portal/dashboard.html')