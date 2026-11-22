import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from leads.models import Lead, CallLog, FollowUp
from loans.models import Bank, LoanScheme, Document, LoanApplication

FIRST = ['Ravi', 'Anita', 'Suresh', 'Priya', 'Karthik', 'Meena', 'Arjun', 'Divya', 'Manoj', 'Kavya']
LAST = ['Kumar', 'Sharma', 'Babu', 'Nair', 'Reddy', 'Iyer', 'Singh', 'Patel']
CITIES = ['Chennai', 'Pune', 'Madurai', 'Kochi', 'Delhi', 'Bengaluru']
LOAN_TYPES = ['personal', 'home', 'business', 'vehicle', 'education']


def make_user(username, password, role, **extra):
    user, created = User.objects.get_or_create(username=username, defaults={'role': role, **extra})
    if created:
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Create demo users, banks and sample data'

    def handle(self, *args, **kwargs):
        admin = make_user('admin', 'Admin@123', 'admin', is_staff=True, is_superuser=True)
        staff = [make_user(f'staff{i}', 'Staff@123', 'staff', first_name=f'Staff {i}')
                 for i in range(1, 6)]

        if Bank.objects.count() == 0:
            for name, rate in [('HDFC Bank', 8.5), ('SBI', 8.3), ('ICICI Bank', 8.7)]:
                bank = Bank.objects.create(name=name, contact_person='Relationship Manager',
                                           phone='9000000000')
                LoanScheme.objects.create(bank=bank, name='Home Loan', interest_rate=rate,
                                          min_amount=500000, max_amount=10000000)
                LoanScheme.objects.create(bank=bank, name='Personal Loan', interest_rate=rate + 3,
                                          min_amount=50000, max_amount=2000000)

        if Lead.objects.filter(phone__startswith='90000').exists():
            self.stdout.write('Demo data already present.')
            return

        random.seed(1)
        now = timezone.now()
        today = timezone.localdate()
        leads = []
        for i in range(200):
            lead = Lead.objects.create(
                name=f'{random.choice(FIRST)} {random.choice(LAST)}',
                phone=f'90000{i:05d}', city=random.choice(CITIES),
                loan_type=random.choice(LOAN_TYPES))
            if i < 100:
                lead.assigned_to = staff[i % len(staff)]
                lead.assigned_date = today
                lead.save()
            leads.append(lead)

        # call history for the last 7 days
        for lead in leads[:100]:
            for _ in range(random.randint(0, 2)):
                status = random.choice(['answered', 'interested', 'not_interested', 'not_reachable'])
                call = CallLog.objects.create(lead=lead, staff=lead.assigned_to, status=status,
                                              remarks='Demo call')
                CallLog.objects.filter(pk=call.pk).update(
                    called_at=now - timedelta(days=random.randint(0, 6), hours=random.randint(0, 8)))
                lead.status = {'answered': 'contacted', 'interested': 'interested',
                               'not_interested': 'not_interested'}.get(status, lead.status)
            lead.save()

        interested = [l for l in leads[:100] if l.status == 'interested']
        schemes = list(LoanScheme.objects.select_related('bank'))
        for n, lead in enumerate(interested[:12]):
            FollowUp.objects.create(lead=lead, staff=lead.assigned_to, note='Discuss documents',
                                    scheduled_at=now + timedelta(days=random.randint(-1, 3)))
            doc = Document(lead=lead, doc_type=random.choice(['aadhaar', 'pan', 'salary']),
                           uploaded_by=lead.assigned_to,
                           verification=random.choice(['pending', 'pending', 'verified']))
            doc.file.save('demo.txt', ContentFile(b'Demo document'), save=True)
            scheme = schemes[n % len(schemes)]
            LoanApplication.objects.create(
                lead=lead, bank=scheme.bank, scheme=scheme, staff=lead.assigned_to,
                amount=scheme.min_amount * 2,
                status=['applied', 'under_review', 'approved', 'disbursed', 'rejected'][n % 5])

        self.stdout.write(self.style.SUCCESS('Demo data created.'))