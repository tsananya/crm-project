from django import forms
from .models import User


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput,
                               help_text="Leave blank to keep the current password.")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'daily_target', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        data = super().clean()
        if not self.instance.pk and not data.get('password'):
            self.add_error('password', 'Password is required for a new employee.')
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user