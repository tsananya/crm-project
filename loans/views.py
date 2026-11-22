from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from .forms import BankForm, SchemeForm
from .models import Bank, LoanScheme, Document, LoanApplication


def _form_view(request, form_class, instance, title, back, msg):
    form = form_class(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, msg)
        return redirect(back)
    return render(request, 'admin_portal/form.html', {'form': form, 'title': title, 'back': back})


@admin_required
def bank_list(request):
    return render(request, 'admin_portal/banks.html', {'banks': Bank.objects.all()})


@admin_required
def bank_form(request, pk=None):
    instance = get_object_or_404(Bank, pk=pk) if pk else None
    return _form_view(request, BankForm, instance, 'Bank', 'bank_list', 'Bank saved.')


@admin_required
def scheme_list(request):
    return render(request, 'admin_portal/schemes.html',
                  {'schemes': LoanScheme.objects.select_related('bank')})


@admin_required
def scheme_form(request, pk=None):
    instance = get_object_or_404(LoanScheme, pk=pk) if pk else None
    return _form_view(request, SchemeForm, instance, 'Loan Scheme', 'scheme_list', 'Scheme saved.')


@admin_required
def document_list(request):
    status = request.GET.get('status', 'pending')
    docs = Document.objects.select_related('lead', 'uploaded_by').order_by('-uploaded_at')
    if status:
        docs = docs.filter(verification=status)
    page = Paginator(docs, 25).get_page(request.GET.get('page'))
    return render(request, 'admin_portal/documents.html',
                  {'page': page, 'status': status, 'choices': Document.VERIFY})


@admin_required
def document_verify(request, pk, action):
    if request.method == 'POST' and action in ('verified', 'rejected'):
        doc = get_object_or_404(Document, pk=pk)
        doc.verification = action
        doc.save()
        messages.success(request, f'Document {action}.')
    return redirect('document_list')


@admin_required
def application_list(request):
    status = request.GET.get('status', '')
    apps = LoanApplication.objects.select_related('lead', 'bank', 'scheme', 'staff').order_by('-created_at')
    if status:
        apps = apps.filter(status=status)
    page = Paginator(apps, 25).get_page(request.GET.get('page'))
    return render(request, 'admin_portal/applications.html',
                  {'page': page, 'status': status, 'choices': LoanApplication.STATUS})


@admin_required
def application_update(request, pk):
    if request.method == 'POST':
        app = get_object_or_404(LoanApplication, pk=pk)
        status = request.POST.get('status')
        if status in dict(LoanApplication.STATUS):
            app.status = status
            app.save()
            if status == 'disbursed':
                app.lead.status = 'converted'
                app.lead.save()
            messages.success(request, f'Application moved to {app.get_status_display()}.')
    return redirect('application_list')