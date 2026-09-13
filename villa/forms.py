from django import forms
from .models import BookingInquiry, ContactMessage

class BookingInquiryForm(forms.ModelForm):
    class Meta:
        model = BookingInquiry
        fields = [
            'full_name',
            'email',
            'phone',
            'stay_type',
            'check_in_date',
            'check_out_date',
            'number_of_guests',
            'message',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your Full Name...', 'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your E-mail...', 'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your Phone / WhatsApp...', 'class': 'form-control', 'required': True}),
            'stay_type': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
            'message': forms.Textarea(attrs={'placeholder': 'Preferred dates, meal options, special requirements...', 'rows': 4, 'class': 'form-control'}),
        }


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your Name...', 'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email...', 'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'placeholder': 'Your Phone...', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject...', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message...', 'rows': 4, 'class': 'form-control', 'required': True}),
        }

