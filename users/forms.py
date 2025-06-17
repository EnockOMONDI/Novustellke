
from django.contrib.auth.forms import UserCreationForm
from .models import UserBookings
from django import forms
from django.contrib.auth.models import User
from .models import MICEInquiry, StudentTravelInquiry, NGOTravelInquiry


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-box'}), label='')
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'input-box'}), label='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'input-box'}), label='')
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'input-box'}), label='')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'input-box'}), label='')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'input-box'}), label='')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email






class UserBookingsForm(forms.ModelForm):
    class Meta:
        model = UserBookings
        fields = [
            'full_name',
            'phone_number',
            'number_of_adults',
            'number_of_children',
            'number_of_rooms',
            'include_travelling',
            'special_requests',
            'paid'
        ]



class MICEInquiryForm(forms.ModelForm):
    class Meta:
        model = MICEInquiry
        fields = ['company_name', 'contact_person', 'email', 'phone_number',
                 'event_type', 'attendees', 'event_details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add classes and placeholders to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.replace('_', ' ').title()
            })


class StudentTravelInquiryForm(forms.ModelForm):
    class Meta:
        model = StudentTravelInquiry
        fields = ['school_name', 'contact_person', 'email', 'phone_number',
                 'program_stage', 'number_of_students', 'travel_details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add classes and placeholders to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.replace('_', ' ').title()
            })


class NGOTravelInquiryForm(forms.ModelForm):
    class Meta:
        model = NGOTravelInquiry
        fields = ['organization_name', 'contact_person', 'email', 'phone_number',
                 'organization_type', 'travel_purpose', 'number_of_travelers',
                 'travel_details', 'sustainability_requirements']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add classes and placeholders to form fields
        for field in self.fields:
            if field == 'sustainability_requirements':
                self.fields[field].widget.attrs.update({
                    'class': 'form-check-input'
                })
            else:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.replace('_', ' ').title()
                })