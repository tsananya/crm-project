from django.conf import settings
from django.db import models
from leads.models import Lead


class Bank(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LoanScheme(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='schemes')
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    min_amount = models.IntegerField()
    max_amount = models.IntegerField()

    def __str__(self):
        return f"{self.bank.name} - {self.name}"


class Document(models.Model):
    DOC_TYPES = [('aadhaar', 'Aadhaar'), ('pan', 'PAN'), ('salary', 'Salary Slip'),
                 ('bank_statement', 'Bank Statement'), ('photo', 'Photo'), ('other', 'Other')]
    VERIFY = [('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES)
    file = models.FileField(upload_to='documents/')
    verification = models.CharField(max_length=10, choices=VERIFY, default='pending')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.name} - {self.doc_type}"


class LoanApplication(models.Model):
    STATUS = [('applied', 'Applied'), ('under_review', 'Under Review'),
              ('approved', 'Approved'), ('disbursed', 'Disbursed'),
              ('rejected', 'Rejected'), ('closed', 'Closed')]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='applications')
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    scheme = models.ForeignKey(LoanScheme, on_delete=models.PROTECT)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='applied')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead.name} - {self.bank.name} ({self.status})"
