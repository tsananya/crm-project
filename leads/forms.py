from django import forms
from .models import CallLog, FollowUp
from loans.models import Document, LoanApplication


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-select' if isinstance(f.widget, forms.Select) else 'form-control'


class CallLogForm(StyledForm):
    class Meta:
        model = CallLog
        fields = ['status', 'remarks']
        widgets = {'remarks': forms.Textarea(attrs={'rows': 2})}


class FollowUpForm(StyledForm):
    scheduled_at = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))

    class Meta:
        model = FollowUp
        fields = ['scheduled_at', 'note']


class DocumentForm(StyledForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'file']


class ApplicationForm(StyledForm):
    class Meta:
        model = LoanApplication
        fields = ['scheme', 'amount', 'remarks']
        widgets = {'remarks': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        data = super().clean()
        scheme, amount = data.get('scheme'), data.get('amount')
        if scheme and amount and not (scheme.min_amount <= amount <= scheme.max_amount):
            self.add_error('amount', f'Amount must be between {scheme.min_amount} and {scheme.max_amount} for this scheme.')
        return data