from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import staff_required
from .forms import CallLogForm, FollowUpForm, DocumentForm, ApplicationForm
from .models import Lead, CallLog, FollowUp

STATUS_AFTER_CALL = {'answered': 'contacted', 'interested': 'interested',
                     'not_interested': 'not_interested'}


def _own_lead(request, pk):
    # a staff member can only open leads assigned to them
    return get_object_or_404(Lead, pk=pk, assigned_to=request.user)


@staff_required
def staff_dashboard(request):
    user = request.user
    done = CallLog.objects.filter(staff=user, called_at__date=timezone.localdate()).count()
    target = user.daily_target or 1
    leads = Lead.objects.filter(assigned_to=user).order_by('-assigned_date', 'id')
    status = request.GET.get('status', '')
    if status:
        leads = leads.filter(status=status)
    page = Paginator(leads, 25).get_page(request.GET.get('page'))
    return render(request, 'staff_portal/dashboard.html', {
        'page': page, 'done': done, 'target': user.daily_target,
        'percent': min(100, int(done * 100 / target)),
        'status': status, 'status_choices': Lead.STATUS})


@staff_required
def lead_detail(request, pk):
    lead = _own_lead(request, pk)
    return render(request, 'staff_portal/lead_detail.html', {
        'lead': lead,
        'call_form': CallLogForm(), 'fu_form': FollowUpForm(),
        'doc_form': DocumentForm(), 'app_form': ApplicationForm(),
        'calls': lead.calls.select_related('staff').order_by('-called_at')[:20],
        'followups': lead.followups.order_by('scheduled_at'),
        'documents': lead.documents.order_by('-uploaded_at'),
        'applications': lead.applications.select_related('bank', 'scheme').order_by('-created_at'),
    })


@staff_required
def add_call(request, pk):
    lead = _own_lead(request, pk)
    if request.method == 'POST':
        form = CallLogForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.lead, call.staff = lead, request.user
            call.save()
            new_status = STATUS_AFTER_CALL.get(call.status)
            if new_status and lead.status != 'converted':
                lead.status = new_status
                lead.save()
            messages.success(request, 'Call recorded.')
        else:
            messages.error(request, 'Could not save the call. Check the form.')
    return redirect('lead_detail', pk=pk)


@staff_required
def add_followup(request, pk):
    lead = _own_lead(request, pk)
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            fu = form.save(commit=False)
            fu.lead, fu.staff = lead, request.user
            fu.save()
            messages.success(request, 'Follow-up scheduled.')
        else:
            messages.error(request, 'Enter a valid follow-up date and time.')
    return redirect('lead_detail', pk=pk)


@staff_required
def upload_document(request, pk):
    lead = _own_lead(request, pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.lead, doc.uploaded_by = lead, request.user
            doc.save()
            messages.success(request, 'Document uploaded. Waiting for verification.')
        else:
            messages.error(request, 'Could not upload the document.')
    return redirect('lead_detail', pk=pk)


@staff_required
def add_application(request, pk):
    lead = _own_lead(request, pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.lead, app.staff, app.bank = lead, request.user, form.cleaned_data['scheme'].bank
            app.save()
            messages.success(request, 'Loan application created.')
        else:
            messages.error(request, ' '.join(e for errs in form.errors.values() for e in errs))
    return redirect('lead_detail', pk=pk)


@staff_required
def my_followups(request):
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    pending = FollowUp.objects.filter(staff=request.user, done=False).select_related('lead').order_by('scheduled_at')
    return render(request, 'staff_portal/followups.html', {
        'overdue': pending.filter(scheduled_at__lt=start),
        'today': pending.filter(scheduled_at__gte=start, scheduled_at__lt=end),
        'upcoming': pending.filter(scheduled_at__gte=end)})


@staff_required
def followup_done(request, pk):
    if request.method == 'POST':
        fu = get_object_or_404(FollowUp, pk=pk, staff=request.user)
        fu.done = True
        fu.save()
        messages.success(request, 'Follow-up marked done.')
    return redirect('my_followups')


@staff_required
def performance(request):
    user = request.user
    today = timezone.localdate()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = [CallLog.objects.filter(staff=user, called_at__date=d).count() for d in dates]
    all_calls = CallLog.objects.filter(staff=user)
    return render(request, 'staff_portal/performance.html', {
        'labels': [d.strftime('%d %b') for d in dates], 'counts': counts,
        'today_calls': counts[-1], 'target': user.daily_target,
        'total_calls': all_calls.count(),
        'interested': all_calls.filter(status='interested').count(),
        'applications': user.loanapplication_set.count()})