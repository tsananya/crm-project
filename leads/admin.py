from django.contrib import admin
from .models import Lead, CallLog, FollowUp

admin.site.register(Lead)
admin.site.register(CallLog)
admin.site.register(FollowUp)
