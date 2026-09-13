import uuid
from django.db import models

class BookingInquiry(models.Model):
    STAY_CHOICES = [
        ('visit', 'Villa Visit / Site Inspection Appointment'),
        ('overnight', 'Overnight Stay (Check-in 12:00 PM, Check-out 11:00 AM)'),
        ('day_outing', 'Day Outing (Lunch, High Tea / Dinner, Pool)'),
        ('celebration', 'Family Celebration / Get-together / Event'),
    ]

    STATUS_CHOICES = [
        ('new', 'New Inquiry'),
        ('contacted', 'Contacted'),
        ('confirmed', 'Confirmed Booking'),
        ('cancelled', 'Cancelled'),
    ]

    reference_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=150, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=30, verbose_name="Phone / WhatsApp")
    stay_type = models.CharField(max_length=40, choices=STAY_CHOICES, default='overnight', verbose_name="Stay Type")
    check_in_date = models.DateField(null=True, blank=True, verbose_name="Check-in Date")
    check_out_date = models.DateField(null=True, blank=True, verbose_name="Check-out Date")
    number_of_guests = models.PositiveIntegerField(default=6, verbose_name="Guest Count")
    message = models.TextField(blank=True, verbose_name="Requirements & Message")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Status")
    admin_notes = models.TextField(blank=True, verbose_name="Internal Staff Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "Booking Inquiry"
        verbose_name_plural = "Booking Inquiries"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_id:
            # Generate clean reference ID like GV-8492
            short_id = uuid.uuid4().hex[:6].upper()
            self.reference_id = f"GV-{short_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_id} - {self.full_name} ({self.get_stay_type_display()})"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Mark as Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Received At")

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.full_name} ({self.created_at.strftime('%d %b %Y')})"


class VillaSpace(models.Model):
    CATEGORY_CHOICES = [
        ('outdoor', 'Pool & Outdoors'),
        ('bedrooms', 'Bedrooms & Dorm'),
        ('indoor', 'Living & Kitchen'),
        ('terrace', 'Sky Terraces'),
    ]

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='outdoor')
    subtitle = models.CharField(max_length=100, default='Luxury Feature')
    location_info = models.CharField(max_length=150, default='Grace Ville, Saswad')
    spec_1 = models.CharField(max_length=120, blank=True)
    spec_2 = models.CharField(max_length=120, blank=True)
    spec_3 = models.CharField(max_length=120, blank=True)
    spec_4 = models.CharField(max_length=120, blank=True)
    spec_5 = models.CharField(max_length=120, blank=True)
    image_rel_path = models.CharField(max_length=255, default='assets/images/property-01.jpg')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Villa Space"
        verbose_name_plural = "Villa Spaces"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
