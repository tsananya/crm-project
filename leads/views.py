from datetime import date

import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.decorators import admin_required
from accounts.models import User
from .models import Lead


@admin_required
def lead_list(request):
    leads = Lead.objects.select_related('assigned_to').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    staff = request.GET.get('staff', '')
    if q:
        leads = leads.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    if status:
        leads = leads.filter(status=status)
    if staff == 'none':
        leads = leads.filter(assigned_to__isnull=True)
    elif staff:
        leads = leads.filter(assigned_to_id=staff)

    page = Paginator(leads, 25).get_page(request.GET.get('page'))
    return render(request, 'admin_portal/leads.html', {
        'page': page,
        'q': q, 'status': status, 'staff': staff,
        'status_choices': Lead.STATUS,
        'staff_list': User.objects.filter(role='staff'),
    })


@admin_required
def lead_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        f = request.FILES['file']
        try:
            df = pd.read_csv(f, dtype=str) if f.name.lower().endswith('.csv') \
                else pd.read_excel(f, dtype=str)
        except Exception:
            messages.error(request, 'Could not read the file. Upload a .csv or .xlsx file.')
            return redirect('lead_upload')

        df.columns = [str(c).strip().lower() for c in df.columns]
        if not {'name', 'phone'}.issubset(df.columns):
            messages.error(request, 'File must have at least the columns: name, phone.')
            return redirect('lead_upload')

        valid_types = {key for key, _ in Lead.LOAN_TYPES}
        existing = set(Lead.objects.values_list('phone', flat=True))
        new_leads, skipped = [], 0

        for _, row in df.fillna('').iterrows():
            name = str(row['name']).strip()
            phone = str(row['phone']).strip()
            if not name or not phone or phone in existing:
                skipped += 1
                continue
            existing.add(phone)
            loan_type = str(row.get('loan_type', '')).strip().lower()
            new_leads.append(Lead(
                name=name, phone=phone,
                city=str(row.get('city', '')).strip(),
                loan_type=loan_type if loan_type in valid_types else 'personal',
            ))

        Lead.objects.bulk_create(new_leads)
        messages.success(request, f'{len(new_leads)} leads uploaded, {skipped} skipped '
                                  f'(blank or duplicate phone).')
        return redirect('lead_list')
    return render(request, 'admin_portal/lead_upload.html')


@admin_required
def sample_csv(request):
    content = ("name,phone,city,loan_type\n"
               "Ravi Kumar,9876543210,Chennai,home\n"
               "Anita Sharma,9876501234,Pune,personal\n"
               "Suresh Babu,9123456780,Madurai,business\n")
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_leads.csv"'
    return response


@admin_required
def lead_assign(request):
    today = date.today()
    staff = list(User.objects.filter(role='staff', is_active=True).order_by('username'))
    unassigned_count = Lead.objects.filter(assigned_to__isnull=True).count()

    if request.method == 'POST':
        if not staff:
            messages.error(request, 'No active employees to assign leads to.')
            return redirect('lead_assign')

        capacity = {}
        for s in staff:
            done = Lead.objects.filter(assigned_to=s, assigned_date=today).count()
            capacity[s.id] = max(s.daily_target - done, 0)

        leads = list(Lead.objects.filter(assigned_to__isnull=True).order_by('id'))
        assigned, turn = 0, 0
        for lead in leads:
            available = [s for s in staff if capacity[s.id] > 0]
            if not available:
                break
            s = available[turn % len(available)]
            lead.assigned_to = s
            lead.assigned_date = today
            capacity[s.id] -= 1
            turn += 1
            assigned += 1

        Lead.objects.bulk_update(leads[:assigned], ['assigned_to', 'assigned_date'])
        messages.success(request, f'{assigned} leads assigned. '
                                  f'{len(leads) - assigned} left unassigned.')
        return redirect('lead_assign')

    rows = [(s, Lead.objects.filter(assigned_to=s, assigned_date=today).count()) for s in staff]
    return render(request, 'admin_portal/lead_assign.html', {
        'rows': rows, 'unassigned_count': unassigned_count, 'today': today})