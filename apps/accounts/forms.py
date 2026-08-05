from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=30, required=False)
    agree = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'country', 'profile_image', 'notification_emails', 'notification_sms')
        widgets = {
            'notification_emails': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'notification_sms': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
