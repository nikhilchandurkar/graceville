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

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name (minimum 2 characters).")
        return name

    def clean_phone(self):
        import re
        phone = self.cleaned_data.get('phone', '').strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid phone number (at least 10 digits).")
        return phone

    def clean_check_in_date(self):
        from django.utils import timezone
        date = self.cleaned_data.get('check_in_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past. Please choose today or a future date.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        if check_in and check_out and check_out < check_in:
            self.add_error('check_out_date', "Check-out date cannot be earlier than check-in date.")
        return cleaned_data


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

