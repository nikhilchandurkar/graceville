import os
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def get_receiver_emails():
    """
    Returns list of recipient emails configured via environment or settings.
    Supports comma-separated emails.
    """
    raw_receivers = os.environ.get('NOTIFICATION_RECEIVER_EMAIL') or getattr(settings, 'NOTIFICATION_RECEIVER_EMAIL', 'graceville1911@gmail.com')
    if not raw_receivers:
        return ['graceville1911@gmail.com']
    
    # Split by comma or semicolon and strip whitespace
    emails = [e.strip() for e in raw_receivers.replace(';', ',').split(',') if e.strip()]
    return emails if emails else ['graceville1911@gmail.com']

def send_inquiry_notification(inquiry):
    """
    Sends email notification to the villa owners/managers when a booking inquiry is submitted.
    Also sends confirmation email to the guest if their email is provided.
    """
    receivers = get_receiver_emails()
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Grace Ville <graceville1911@gmail.com>')

    # 1. Email to Villa Management / Host
    subject = f"🔔 New Booking Inquiry: {inquiry.reference_id} - {inquiry.full_name}"
    
    body = f"""Hello Grace Ville Team,

A new booking inquiry has been submitted on the Grace Ville website.

--------------------------------------------------
BOOKING INQUIRY DETAILS
--------------------------------------------------
Reference ID:     {inquiry.reference_id}
Guest Name:       {inquiry.full_name}
Phone / WhatsApp: {inquiry.phone}
Email Address:    {inquiry.email or 'Not provided'}
Stay Package:     {inquiry.get_stay_type_display()}
Check-in Date:    {inquiry.check_in_date or 'Flexible / Not specified'}
Check-out Date:   {inquiry.check_out_date or 'Flexible / Not specified'}
Number of Guests: {inquiry.number_of_guests}
Special Requests:
{inquiry.message or 'None'}

--------------------------------------------------
Submitted at: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Status:       {inquiry.get_status_display()}

To view or manage this booking, log into the Admin Dashboard:
https://your-domain.vercel.app/admin/villa/bookinginquiry/{inquiry.id}/change/

Best regards,
Grace Ville Automated Booking System
Saswad, Udachiwadi, Pune
"""

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=receivers,
            fail_silently=False,
        )
        logger.info(f"Booking inquiry email notification sent to {receivers} for {inquiry.reference_id}")
    except Exception as e:
        logger.error(f"Failed to send booking notification email: {e}")

    # 2. Confirmation Email to the Guest (if valid email provided)
    if inquiry.email and '@' in inquiry.email:
        guest_subject = f"Booking Inquiry Received - Grace Ville Villa (Ref: {inquiry.reference_id})"
        guest_body = f"""Dear {inquiry.full_name},

Thank you for choosing Grace Ville! We have received your booking inquiry and our reservation concierge will reach out to you shortly to confirm your dates and package.

--------------------------------------------------
YOUR INQUIRY SUMMARY
--------------------------------------------------
Booking Reference: {inquiry.reference_id}
Package:           {inquiry.get_stay_type_display()}
Guests:            {inquiry.number_of_guests}
Check-in:          {inquiry.check_in_date or 'To be confirmed'}
Contact Phone:     {inquiry.phone}

--------------------------------------------------
LOCATION & DIRECTIONS
--------------------------------------------------
Grace Ville, Udachiwadi, Saswad, Pune, Maharashtra
Google Maps: https://maps.app.goo.gl/UdachiwadiGraceVille

If you have urgent questions or wish to confirm immediately, connect directly on WhatsApp:
https://wa.me/{getattr(settings, 'WHATSAPP_PHONE', '919876543210')}?text=Hi%20Grace%20Ville%20Team%2C%20inquiring%20about%20Ref%3A%20{inquiry.reference_id}

Warm regards,
The Grace Ville Team
Relax, Celebrate & Reconnect with Nature
"""
        try:
            send_mail(
                subject=guest_subject,
                message=guest_body,
                from_email=from_email,
                recipient_list=[inquiry.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send guest confirmation email: {e}")


def send_contact_message_notification(contact_msg):
    """
    Sends email notification to the villa managers when a general contact message is sent.
    """
    receivers = get_receiver_emails()
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Grace Ville <graceville1911@gmail.com>')

    subject = f"✉️ Contact Message from {contact_msg.full_name}: {contact_msg.subject or 'General Inquiry'}"
    body = f"""Hello Grace Ville Team,

A visitor has submitted a contact message through the Grace Ville website.

Sender Name:  {contact_msg.full_name}
Email:        {contact_msg.email}
Phone:        {contact_msg.phone or 'Not provided'}
Subject:      {contact_msg.subject or 'General Inquiry'}

Message:
--------------------------------------------------
{contact_msg.message}
--------------------------------------------------

Received at: {contact_msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=receivers,
            fail_silently=False,
        )
        logger.info(f"Contact email sent to {receivers}")
    except Exception as e:
        logger.error(f"Failed to send contact notification email: {e}")

