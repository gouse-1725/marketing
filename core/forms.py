from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Address
import re


class MobileNumberForm(forms.Form):
    mobile_no = forms.CharField(
        max_length=15,
        required=True,
        label="Mobile Number",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your mobile number", "class": "form-control"}
        ),
    )

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get("mobile_no")
        if not re.match(r"^\+?\d{10,15}$", mobile_no):
            raise forms.ValidationError(
                "Enter a valid mobile number (10-15 digits, optional '+' prefix)."
            )
        return mobile_no


class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        required=True,
        label="OTP Code",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter OTP", "class": "form-control"}
        ),
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter your email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your last name"}
            ),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=200, required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")


class ForgotPasswordForm(forms.Form):
    mobile_no = forms.CharField(max_length=15, required=True, label="Mobile Number")
    email = forms.EmailField(required=False, label="Email (if no email is associated)")

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get("mobile_no")
        if not re.match(r"^\+?\d{10,15}$", mobile_no):
            raise forms.ValidationError(
                "Enter a valid mobile number (10-15 digits, optional '+' prefix)."
            )
        return mobile_no


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, required=True, label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line', 'city', 'state', 'pincode']
