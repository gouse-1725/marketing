from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('mobile_no', 'email', 'first_name', 'last_name')

    mobile_no = forms.CharField(label='Mobile Number', max_length=15)
    email = forms.EmailField(required=False, label='Email ')
    first_name = forms.CharField(required=False, label='First Name (Optional)')
    last_name = forms.CharField(required=False, label='Last Name (Optional)')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get('mobile_no')
        if not re.match(r'^\+?\d{10,15}$', mobile_no):
            raise forms.ValidationError("Enter a valid mobile number (10-15 digits, optional '+' prefix).")
        if CustomUser.objects.filter(mobile_no=mobile_no).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mobile_no

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data

    def save(self, commit=True):
        mobile_no = self.cleaned_data.get('mobile_no')
        password = self.cleaned_data.get('password1')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        user = CustomUser.objects.create_user(
            mobile_no=mobile_no,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return user

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label='Your Name')
    email = forms.EmailField(required=True, label='Your Email')
    subject = forms.CharField(max_length=200, required=True, label='Subject')
    message = forms.CharField(widget=forms.Textarea, required=True, label='Message')

class ForgotPasswordForm(forms.Form):
    mobile_no = forms.CharField(max_length=15, required=True, label='Mobile Number')
    email = forms.EmailField(required=False, label="Email (if no email is associated)")

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get('mobile_no')
        if not re.match(r'^\+?\d{10,15}$', mobile_no):
            raise forms.ValidationError("Enter a valid mobile number (10-15 digits, optional '+' prefix).")
        return mobile_no

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label='OTP Code')

class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, required=True, label='New Password')
    new_password2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm New Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data