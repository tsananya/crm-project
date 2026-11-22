from django.conf import settings
from django.db import models

class Lead(models.Model):
    LOAN_TYPES = [('personal', 'Personal'), ('home', 'Home'), ('business', 'Business'),
                  ('vehicle', 'Vehicle'), ('education', 'Education')]
    STATUS = [('new', 'New'), ('contacted', 'Contacted'), ('interested', 'Interested'),
              ('not_interested', 'Not Interested'), ('converted', 'Converted')]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=60, blank=True)
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES, default='personal')
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='leads')
    assigned_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class CallLog(models.Model):
    CALL_STATUS = [('answered', 'Answered'), ('not_reachable', 'Not Reachable'),
                   ('interested', 'Interested'), ('not_interested', 'Not Interested')]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='calls')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=CALL_STATUS)
    remarks = models.TextField(blank=True)
    called_at = models.DateTimeField(auto_now_add=True)


class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    note = models.CharField(max_length=200, blank=True)
    done = models.BooleanField(default=False)
