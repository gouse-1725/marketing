from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    mobile_no = forms.CharField(max_length=15, required=True)
    gift_code = forms.CharField(max_length=50, required=True)
    introducer_id = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        to_field_name='username',
        label="Introducer ID",
        required=False,
        empty_label="None (First User)"
    )
    placed_under_id = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        to_field_name='username',
        label="Placed Under ID",
        required=False,
        empty_label="None (First User)"
    )
    position = forms.ChoiceField(choices=[('', 'None'), ('left', 'Left'), ('right', 'Right')], required=False)
    terms_agreed = forms.BooleanField(required=True, label="I agree to the terms and conditions")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'mobile_no', 'gift_code', 'introducer_id', 'placed_under_id', 'position', 'password1', 'password2', 'terms_agreed')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields['introducer_id'].initial = user
            self.fields['introducer_id'].disabled = True  # Lock introducer to current user

    def clean_introducer_id(self):
        introducer = self.cleaned_data.get('introducer_id')
        if CustomUser.objects.exists() and not introducer:
            raise forms.ValidationError("Please select a valid Introducer ID")
        return introducer or self.user

    def clean_placed_under_id(self):
        parent = self.cleaned_data.get('placed_under_id')
        if CustomUser.objects.exists() and not parent:
            raise forms.ValidationError("Please select a valid Placed Under ID")
        return parent

    def clean_position(self):
        position = self.cleaned_data.get('position')
        parent = self.cleaned_data.get('placed_under_id')
        if parent:
            if not position:
                raise forms.ValidationError("Please select a position (Left or Right)")
            # Check if position is already taken
            if CustomUser.objects.filter(parent=parent, position=position).exists():
                raise forms.ValidationError(f"The {position} position under this parent is already taken")
        return position

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        mobile_no = cleaned_data.get('mobile_no')
        gift_code = cleaned_data.get('gift_code')

        if username and CustomUser.objects.filter(username=username).exists():
            self.add_error('username', "A user with that username already exists.")
        if mobile_no and CustomUser.objects.filter(mobile_no=mobile_no).exists():
            self.add_error('mobile_no', "This mobile number is already in use.")
        if gift_code and CustomUser.objects.filter(gift_code=gift_code).exists():
            self.add_error('gift_code', "This gift code is already in use.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.mobile_no = self.cleaned_data['mobile_no']
        user.gift_code = self.cleaned_data['gift_code']
        user.introducer = self.cleaned_data['introducer_id']
        user.parent = self.cleaned_data['placed_under_id']
        user.position = self.cleaned_data['position']
        if commit:
            user.save()
        return user

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)