from django.db.models import Q
from django.utils import timezone
from leads.models import Lead, CallLog
from loans.models import LoanApplication, Document
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import admin_required, staff_required
from .forms import EmployeeForm
from .models import User
from django.contrib.auth import views as auth_views


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
    today = timezone.localdate()
    staff = User.objects.filter(role='staff', is_active=True).annotate(
        calls=Count('calllog', filter=Q(calllog__called_at__date=today))).order_by('username')
    calls_today = CallLog.objects.filter(called_at__date=today)
    app_counts = [(label, LoanApplication.objects.filter(status=key).count())
                  for key, label in LoanApplication.STATUS]
    return render(request, 'admin_portal/dashboard.html', {
        'total_leads': Lead.objects.count(),
        'unassigned': Lead.objects.filter(assigned_to__isnull=True).count(),
        'calls_today': calls_today.count(),
        'interested_today': calls_today.filter(status='interested').count(),
        'pending_docs': Document.objects.filter(verification='pending').count(),
        'applications': LoanApplication.objects.count(),
        'app_counts': app_counts,
        'staff_rows': [(s.username, s.calls, s.daily_target) for s in staff],
        'labels': [s.username for s in staff],
        'counts': [s.calls for s in staff],
        'targets': [s.daily_target for s in staff],
    })

@staff_required
def staff_dashboard(request):
    return render(request, 'staff_portal/dashboard.html')


@admin_required
def employee_list(request):
    employees = User.objects.filter(role='staff').annotate(
        lead_count=Count('leads')).order_by('username')
    return render(request, 'admin_portal/employees.html', {'employees': employees})


@admin_required
def employee_form(request, pk=None):
    instance = get_object_or_404(User, pk=pk, role='staff') if pk else None
    form = EmployeeForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Employee saved.')
        return redirect('employee_list')
    return render(request, 'admin_portal/employee_form.html',
                  {'form': form, 'instance': instance})


@admin_required
def employee_toggle(request, pk):
    if request.method == 'POST':
        emp = get_object_or_404(User, pk=pk, role='staff')
        emp.is_active = not emp.is_active
        emp.save()
        messages.success(request, f'{emp.username} is now {"active" if emp.is_active else "deactivated"}.')
    return redirect('employee_list')

def mobile_entry(request):
    request.session['mobile'] = True
    return redirect('home')


def desktop_entry(request):
    request.session.pop('mobile', None)
    return redirect('home')

class SmartLoginView(auth_views.LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # a plain /login/ visit (no "next") resets to the desktop layout
        if request.method == 'GET' and 'next' not in request.GET:
            request.session.pop('mobile', None)
        return super().dispatch(request, *args, **kwargs)