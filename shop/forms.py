from django import forms
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )

    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name, user.last_name = self.cleaned_data['full_name'].split(' ', 1)
        if commit:
            user.save()
        return user
