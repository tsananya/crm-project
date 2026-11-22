from django.contrib import admin
from .models import Bank, LoanScheme, Document, LoanApplication

admin.site.register(Bank)
admin.site.register(LoanScheme)
admin.site.register(Document)
admin.site.register(LoanApplication)