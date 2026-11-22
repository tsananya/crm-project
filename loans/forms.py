from django import forms
from .models import Bank, LoanScheme


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs['class'] = 'form-check-input'
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'form-select'
            else:
                f.widget.attrs['class'] = 'form-control'


class BankForm(StyledForm):
    class Meta:
        model = Bank
        fields = ['name', 'contact_person', 'phone', 'is_active']


class SchemeForm(StyledForm):
    class Meta:
        model = LoanScheme
        fields = ['bank', 'name', 'interest_rate', 'min_amount', 'max_amount']