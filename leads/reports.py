import csv
from datetime import date, timedelta

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import admin_required
from accounts.models import User


def _parse(value, default):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


@admin_required
def report(request):
    today = timezone.localdate()
    start = _parse(request.GET.get('from'), today - timedelta(days=6))
    end = _parse(request.GET.get('to'), today)
    emp = request.GET.get('staff', '')

    staff = User.objects.filter(role='staff').order_by('username')
    if emp:
        staff = staff.filter(pk=emp)

    calls = Q(calllog__called_at__date__gte=start, calllog__called_at__date__lte=end)
    apps = Q(loanapplication__created_at__date__gte=start,
             loanapplication__created_at__date__lte=end)

    data = staff.annotate(
        total=Count('calllog', filter=calls, distinct=True),
        interested=Count('calllog', filter=calls & Q(calllog__status='interested'), distinct=True),
        not_interested=Count('calllog', filter=calls & Q(calllog__status='not_interested'), distinct=True),
        not_reachable=Count('calllog', filter=calls & Q(calllog__status='not_reachable'), distinct=True),
        applications=Count('loanapplication', filter=apps, distinct=True),
        disbursed=Count('loanapplication', filter=apps & Q(loanapplication__status='disbursed'), distinct=True),
    )

    rows = [[s.username, s.total, s.interested, s.not_interested,
             s.not_reachable, s.applications, s.disbursed] for s in data]

    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{start}_{end}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Employee', 'Calls', 'Interested', 'Not interested',
                         'Not reachable', 'Applications', 'Disbursed'])
        writer.writerows(rows)
        return response

    return render(request, 'admin_portal/report.html', {
        'rows': rows, 'start': start, 'end': end, 'emp': emp,
        'staff_list': User.objects.filter(role='staff').order_by('username'),
        'totals': [sum(r[i] for r in rows) for i in range(1, 7)],
    })