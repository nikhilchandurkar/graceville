import os
import logging
import urllib.parse
from datetime import datetime, time, timedelta
from django.core.mail import EmailMultiAlternatives
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
    
    emails = [e.strip() for e in raw_receivers.replace(';', ',').split(',') if e.strip()]
    return emails if emails else ['graceville1911@gmail.com']


def calculate_booking_datetimes(inquiry):
    """
    Calculates start and end datetime in UTC for calendar invites based on check-in/out dates and stay type.
    Assumes Indian Standard Time (IST, UTC+05:30).
    """
    check_in = inquiry.check_in_date
    if not check_in:
        check_in = datetime.now().date() + timedelta(days=1)
    
    stay_type = inquiry.stay_type

    if stay_type == 'visit':
        # 1-hour site visit appointment
        ist_start = datetime.combine(check_in, time(11, 0))
        ist_end = datetime.combine(check_in, time(12, 30))
    elif stay_type == 'day_outing':
        # Day pass: 10:00 AM to 6:00 PM
        ist_start = datetime.combine(check_in, time(10, 0))
        ist_end = datetime.combine(check_in, time(18, 0))
    elif stay_type == 'celebration':
        ist_start = datetime.combine(check_in, time(12, 0))
        if inquiry.check_out_date and inquiry.check_out_date > check_in:
            ist_end = datetime.combine(inquiry.check_out_date, time(11, 0))
        else:
            ist_end = datetime.combine(check_in, time(22, 0))
    else:
        # Standard overnight stay: 12:00 PM check-in, 11:00 AM next day check-out
        ist_start = datetime.combine(check_in, time(12, 0))
        if inquiry.check_out_date and inquiry.check_out_date > check_in:
            ist_end = datetime.combine(inquiry.check_out_date, time(11, 0))
        else:
            ist_end = datetime.combine(check_in + timedelta(days=1), time(11, 0))

    # Convert IST (UTC+05:30) to UTC
    ist_offset = timedelta(hours=5, minutes=30)
    utc_start = ist_start - ist_offset
    utc_end = ist_end - ist_offset

    return ist_start, ist_end, utc_start, utc_end


def get_calendar_details(inquiry):
    """
    Shared title, details and location string for calendar APIs.
    """
    title = f"Grace Ville Stay - {inquiry.get_stay_type_display()} (Ref: {inquiry.reference_id})"
    details = (
        f"Grace Ville Luxury Private Villa\n"
        f"Booking Reference: {inquiry.reference_id}\n"
        f"Guest Name: {inquiry.full_name}\n"
        f"Guests: {inquiry.number_of_guests}\n"
        f"Stay Package: {inquiry.get_stay_type_display()}\n"
        f"Phone / WhatsApp: {inquiry.phone}\n\n"
        f"Location: Udachiwadi, Saswad, Pune (33 km from Pune near Purandar Airport)\n"
        f"Google Maps Directions: https://maps.app.goo.gl/XPxZYJUyNyA1UPX79\n"
        f"Host Concierge: +91 77689 56163 / graceville1911@gmail.com"
    )
    location = "Grace Ville, Udachiwadi, Saswad, Pune, Maharashtra 412301"
    return title, details, location


def get_google_calendar_url(inquiry):
    """
    Generates a free one-click Add to Google Calendar direct Web URL.
    Includes guest email pre-invitation if provided.
    """
    ist_start, ist_end, utc_start, utc_end = calculate_booking_datetimes(inquiry)
    start_str = utc_start.strftime('%Y%m%dT%H%M%SZ')
    end_str = utc_end.strftime('%Y%m%dT%H%M%SZ')
    title, details, location = get_calendar_details(inquiry)

    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': f"{start_str}/{end_str}",
        'details': details,
        'location': location,
    }
    if inquiry.email and '@' in inquiry.email:
        params['add'] = inquiry.email

    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def get_outlook_calendar_url(inquiry):
    """
    Generates a free one-click Add to Microsoft Outlook / Office 365 Calendar Web URL.
    """
    ist_start, ist_end, utc_start, utc_end = calculate_booking_datetimes(inquiry)
    start_iso = utc_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_iso = utc_end.strftime('%Y-%m-%dT%H:%M:%SZ')
    title, details, location = get_calendar_details(inquiry)

    params = {
        'path': '/calendar/action/compose',
        'rru': 'addevent',
        'subject': title,
        'startdt': start_iso,
        'enddt': end_iso,
        'body': details,
        'location': location,
    }
    return f"https://outlook.live.com/calendar/0/deeplink/compose?{urllib.parse.urlencode(params)}"


def get_yahoo_calendar_url(inquiry):
    """
    Generates a free one-click Add to Yahoo Calendar Web URL.
    """
    ist_start, ist_end, utc_start, utc_end = calculate_booking_datetimes(inquiry)
    start_str = utc_start.strftime('%Y%m%dT%H%M%SZ')
    end_str = utc_end.strftime('%Y%m%dT%H%M%SZ')
    title, details, location = get_calendar_details(inquiry)

    params = {
        'v': '60',
        'view': 'd',
        'type': '20',
        'title': title,
        'st': start_str,
        'et': end_str,
        'desc': details,
        'in_loc': location,
    }
    return f"https://calendar.yahoo.com/?{urllib.parse.urlencode(params)}"


def get_device_calendar_url(inquiry):
    """
    Direct endpoint URL on Grace Ville domain that serves the .ics file.
    Tapping this URL on iPhone Safari or Android immediately opens the native Calendar app.
    """
    site_url = os.environ.get('SITE_URL', 'https://graceville.vercel.app').rstrip('/')
    return f"{site_url}/booking/{inquiry.reference_id}/calendar.ics"


def generate_ics_invite(inquiry):
    """
    Generates RFC 5545 iCalendar (.ics) content for Apple Calendar, Outlook, and Google Calendar.
    """
    ist_start, ist_end, utc_start, utc_end = calculate_booking_datetimes(inquiry)
    now_utc_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    start_str = utc_start.strftime('%Y%m%dT%H%M%SZ')
    end_str = utc_end.strftime('%Y%m%dT%H%M%SZ')

    summary = f"Grace Ville Stay - {inquiry.reference_id}"
    desc = (
        f"Grace Ville Luxury Private Villa Booking\\n"
        f"Reference: {inquiry.reference_id}\\n"
        f"Guest: {inquiry.full_name}\\n"
        f"Package: {inquiry.get_stay_type_display()}\\n"
        f"Guests: {inquiry.number_of_guests}\\n"
        f"Concierge WhatsApp: +91 77689 56163\\n"
        f"Location: Udachiwadi, Saswad, Pune"
    )
    location = "Grace Ville, Udachiwadi, Saswad, Pune, Maharashtra 412301"
    guest_email = inquiry.email if (inquiry.email and '@' in inquiry.email) else 'guest@graceville.in'

    ics_body = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Grace Ville Luxury Villa//Booking Confirmation//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{inquiry.reference_id}-{start_str}@graceville.in
DTSTAMP:{now_utc_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{summary}
DESCRIPTION:{desc}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
ORGANIZER;CN="Grace Ville Reservations":mailto:graceville1911@gmail.com
ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN="{inquiry.full_name}":mailto:{guest_email}
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Upcoming Stay Reminder: Grace Ville
TRIGGER:-PT24H
END:VALARM
END:VEVENT
END:VCALENDAR""".replace("\r\n", "\n").replace("\n", "\r\n")

    return ics_body


def render_guest_email_html(inquiry, gcal_url, outlook_url, yahoo_url, device_cal_url):
    """
    Renders clean, luxury responsive HTML email for the guest confirmation.
    Includes multi-calendar quick actions (Google, Apple/Device, Outlook, Yahoo).
    """
    check_in_display = inquiry.check_in_date.strftime('%A, %d %B %Y') if inquiry.check_in_date else 'Flexible / To be confirmed'
    check_out_display = inquiry.check_out_date.strftime('%A, %d %B %Y') if inquiry.check_out_date else (
        'Same Day' if inquiry.stay_type in ['day_outing', 'visit'] else 'Next Day 11:00 AM'
    )
    wa_phone = getattr(settings, 'WHATSAPP_PHONE', '917768956163').replace('+', '').replace(' ', '')
    wa_url = f"https://wa.me/{wa_phone}?text=" + urllib.parse.quote(f"Hi Grace Ville Team, inquiring about my booking {inquiry.reference_id}")
    maps_url = "https://maps.app.goo.gl/XPxZYJUyNyA1UPX79"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grace Ville Booking Confirmation</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 25px 10px;">
    <tr>
      <td align="center">
        <!-- Main Email Container -->
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
          
          <!-- Brand Header -->
          <tr>
            <td style="background-color: #1e1e1e; padding: 32px 25px; text-align: center; border-bottom: 4px solid #f35525;">
              <span style="display: inline-block; background-color: #f35525; color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 14px; border-radius: 20px; margin-bottom: 12px;">Reservation Inquiry</span>
              <h1 style="color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: 2px; margin: 0; text-transform: uppercase;">GRACE VILLE</h1>
              <p style="color: #9ca3af; font-size: 12px; letter-spacing: 1.5px; margin: 6px 0 0 0; text-transform: uppercase;">Private Luxury Villa &bull; Saswad, Pune</p>
            </td>
          </tr>

          <!-- Hero Greeting -->
          <tr>
            <td style="padding: 30px 30px 20px 30px;">
              <h2 style="color: #111827; font-size: 20px; font-weight: 700; margin: 0 0 10px 0;">Dear {inquiry.full_name},</h2>
              <p style="color: #4b5563; font-size: 15px; line-height: 1.6; margin: 0;">
                Thank you for choosing <strong>Grace Ville</strong>. We have successfully received your booking inquiry. Our reservation concierge will contact you shortly to finalize your stay details and confirm your reservation.
              </p>
            </td>
          </tr>

          <!-- Booking Details Card -->
          <tr>
            <td style="padding: 0 30px 20px 30px;">
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <tr>
                  <td colspan="2" style="background-color: #f3f4f6; padding: 12px 18px; border-bottom: 1px solid #e5e7eb;">
                    <strong style="color: #1f2937; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Inquiry Reference Summary</strong>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; width: 40%;">Reference ID</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #f35525; font-size: 15px; font-weight: 700;">{inquiry.reference_id}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">Package</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px; font-weight: 600;">{inquiry.get_stay_type_display()}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">Check-in</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px; font-weight: 500;">{check_in_display}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">Check-out</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px; font-weight: 500;">{check_out_display}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">Number of Guests</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px; font-weight: 500;">{inquiry.number_of_guests} Guests</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">Contact Phone</td>
                  <td style="padding: 12px 18px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px;">{inquiry.phone}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 18px; color: #6b7280; font-size: 14px;">Special Requests</td>
                  <td style="padding: 12px 18px; color: #111827; font-size: 14px; font-style: italic;">{inquiry.message or 'None specified'}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Free Calendar Notification & Quick Action Buttons -->
          <tr>
            <td style="padding: 10px 30px 25px 30px; text-align: center;">
              <p style="color: #374151; font-size: 14px; font-weight: 700; margin: 0 0 15px 0;">Add to Your Calendar (Free 1-Tap Sync):</p>
              
              <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto; width: 100%;">
                <!-- Google Calendar Button -->
                <tr>
                  <td align="center" style="padding-bottom: 10px;">
                    <a href="{gcal_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #f35525; color: #ffffff; text-decoration: none; padding: 13px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center; box-shadow: 0 2px 8px rgba(243, 85, 37, 0.3);">
                      Add to Google Calendar
                    </a>
                  </td>
                </tr>
                <!-- Apple / iPhone / Native Device Calendar Button -->
                <tr>
                  <td align="center" style="padding-bottom: 10px;">
                    <a href="{device_cal_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #374151; color: #ffffff; text-decoration: none; padding: 13px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center;">
                      Add to Apple / Device Calendar (.ics)
                    </a>
                  </td>
                </tr>
                <!-- WhatsApp Concierge Button -->
                <tr>
                  <td align="center" style="padding-bottom: 10px;">
                    <a href="{wa_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #25d366; color: #ffffff; text-decoration: none; padding: 13px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center; box-shadow: 0 2px 8px rgba(37, 211, 102, 0.3);">
                      Chat on WhatsApp Concierge
                    </a>
                  </td>
                </tr>
                <!-- Directions on Google Maps -->
                <tr>
                  <td align="center">
                    <a href="{maps_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #1e1e1e; color: #ffffff; text-decoration: none; padding: 13px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center;">
                      Directions on Google Maps
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Other Calendars (Outlook & Yahoo) -->
              <p style="color: #6b7280; font-size: 12px; margin: 15px 0 0 0;">
                Other Calendars: &nbsp;
                <a href="{outlook_url}" target="_blank" style="color: #0078d4; text-decoration: underline; font-weight: 600;">Add to Outlook</a> &nbsp;|&nbsp;
                <a href="{yahoo_url}" target="_blank" style="color: #6001d2; text-decoration: underline; font-weight: 600;">Add to Yahoo</a>
              </p>
              <p style="color: #9ca3af; font-size: 11px; margin: 8px 0 0 0;">
                An automated <strong>invite.ics</strong> calendar file is also attached to this email.
              </p>
            </td>
          </tr>

          <!-- Villa Key Highlights -->
          <tr>
            <td style="padding: 20px 30px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb;">
              <h3 style="color: #111827; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px 0;">What Awaits You at Grace Ville</h3>
              <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding: 4px 0; color: #4b5563; font-size: 13px;">&bull; <strong>Private Swimming Pool:</strong> With cascading waterfall feature &amp; mountain views</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #4b5563; font-size: 13px;">&bull; <strong>Accommodations:</strong> 3 AC bedrooms + 1 AC dorm + 5 washrooms + 3 kitchens</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #4b5563; font-size: 13px;">&bull; <strong>Entertainment:</strong> JBL music system, lawn space &amp; rooftop mountain terraces</td>
                </tr>
                <tr>
                  <td style="padding: 4px 0; color: #4b5563; font-size: 13px;">&bull; <strong>Location:</strong> Udachiwadi, Saswad &mdash; only 33 km from Pune near Purandar Airport</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 30px; text-align: center; background-color: #1e1e1e; color: #9ca3af; font-size: 12px; line-height: 1.6;">
              <p style="margin: 0 0 6px 0; font-weight: 700; color: #ffffff; font-size: 14px;">GRACE VILLE</p>
              <p style="margin: 0 0 6px 0;">Udachiwadi, Saswad, Pune, Maharashtra 412301</p>
              <p style="margin: 0 0 10px 0;">Concierge: +91 77689 56163 | Owner: +91 88880 75454</p>
              <p style="margin: 0; color: #6b7280; font-size: 11px;">&copy; 2026 Grace Ville. All rights reserved.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


def render_host_email_html(inquiry, gcal_url, outlook_url, device_cal_url):
    """
    Renders clean, luxury responsive HTML email for the villa host/team notification.
    """
    check_in_display = inquiry.check_in_date.strftime('%A, %d %B %Y') if inquiry.check_in_date else 'Flexible / Unspecified'
    check_out_display = inquiry.check_out_date.strftime('%A, %d %B %Y') if inquiry.check_out_date else 'Unspecified'
    wa_clean = inquiry.phone.replace('+', '').replace('-', '').replace(' ', '')
    if len(wa_clean) == 10:
        wa_clean = f"91{wa_clean}"
    guest_wa_url = f"https://wa.me/{wa_clean}?text=" + urllib.parse.quote(f"Hello {inquiry.full_name}, thank you for your inquiry for Grace Ville (Ref: {inquiry.reference_id}).")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>New Booking Inquiry: {inquiry.reference_id}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 25px 10px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
          
          <!-- Header -->
          <tr>
            <td style="background-color: #1e1e1e; padding: 28px 25px; text-align: center; border-bottom: 4px solid #f35525;">
              <span style="display: inline-block; background-color: #f35525; color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 14px; border-radius: 20px; margin-bottom: 10px;">Host Alert</span>
              <h1 style="color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: 1.5px; margin: 0; text-transform: uppercase;">NEW BOOKING INQUIRY</h1>
              <p style="color: #9ca3af; font-size: 12px; margin: 6px 0 0 0;">Received at {inquiry.created_at.strftime('%d %B %Y, %I:%M %p')}</p>
            </td>
          </tr>

          <!-- Guest Summary Card -->
          <tr>
            <td style="padding: 25px 30px 15px 30px;">
              <h2 style="color: #111827; font-size: 18px; font-weight: 700; margin: 0 0 8px 0;">Guest: {inquiry.full_name}</h2>
              <p style="color: #4b5563; font-size: 14px; margin: 0;">A new reservation inquiry has been submitted through the Grace Ville website.</p>
            </td>
          </tr>

          <!-- Key Details Table -->
          <tr>
            <td style="padding: 0 30px 20px 30px;">
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px; width: 38%;">Reference ID</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #f35525; font-size: 14px; font-weight: 700;">{inquiry.reference_id}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Package</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{inquiry.get_stay_type_display()}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Check-in Date</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{check_in_display}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Check-out Date</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{check_out_display}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Guest Count</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{inquiry.number_of_guests} Guests</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Guest Phone</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">
                    <a href="tel:{inquiry.phone}" style="color: #111827; text-decoration: none;">{inquiry.phone}</a>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Guest Email</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px;">{inquiry.email or 'Not provided'}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; color: #6b7280; font-size: 13px;">Guest Message</td>
                  <td style="padding: 10px 16px; color: #111827; font-size: 13px; font-style: italic;">{inquiry.message or 'None'}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Quick Host Actions -->
          <tr>
            <td style="padding: 5px 30px 25px 30px; text-align: center;">
              <table border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto; width: 100%;">
                <tr>
                  <td align="center" style="padding-bottom: 10px;">
                    <a href="{guest_wa_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #25d366; color: #ffffff; text-decoration: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center;">
                      Message Guest on WhatsApp
                    </a>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding-bottom: 10px;">
                    <a href="{gcal_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #f35525; color: #ffffff; text-decoration: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center;">
                      Add to Host Google Calendar
                    </a>
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <a href="{device_cal_url}" target="_blank" style="display: block; width: 85%; max-width: 320px; background-color: #374151; color: #ffffff; text-decoration: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center;">
                      Download Host .ICS Calendar File
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 30px; text-align: center; background-color: #1e1e1e; color: #9ca3af; font-size: 11px;">
              <p style="margin: 0;">Grace Ville Automated Reservation System &bull; Udachiwadi, Saswad</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


def render_contact_message_html(contact_msg):
    """
    Renders clean responsive HTML for a contact form submission.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contact Message from {contact_msg.full_name}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748;">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 25px 10px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
          
          <td style="background-color: #1e1e1e; padding: 24px 25px; text-align: center; border-bottom: 4px solid #f35525;">
            <span style="display: inline-block; background-color: #f35525; color: #ffffff; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">Contact Inquiry</span>
            <h1 style="color: #ffffff; font-size: 22px; font-weight: 800; margin: 0; text-transform: uppercase;">Grace Ville Contact Message</h1>
          </td>

          <tr>
            <td style="padding: 25px 30px;">
              <p style="margin: 0 0 16px 0; color: #374151; font-size: 15px;">A new message has been submitted via the website contact form:</p>
              
              <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 20px;">
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px; width: 35%;">Sender Name</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{contact_msg.full_name}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Email Address</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px;"><a href="mailto:{contact_msg.email}">{contact_msg.email}</a></td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Phone Number</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px;">{contact_msg.phone or 'Not provided'}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 13px;">Subject</td>
                  <td style="padding: 10px 16px; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 13px; font-weight: 600;">{contact_msg.subject or 'General Inquiry'}</td>
                </tr>
                <tr>
                  <td style="padding: 12px 16px; color: #6b7280; font-size: 13px; vertical-align: top;">Message</td>
                  <td style="padding: 12px 16px; color: #111827; font-size: 13px; line-height: 1.5; white-space: pre-line;">{contact_msg.message}</td>
                </tr>
              </table>

              <p style="margin: 0; color: #9ca3af; font-size: 12px;">Received on {contact_msg.created_at.strftime('%d %B %Y at %I:%M %p')}</p>
            </td>
          </tr>

          <tr>
            <td style="padding: 16px 30px; text-align: center; background-color: #1e1e1e; color: #9ca3af; font-size: 11px;">
              <p style="margin: 0;">Grace Ville Luxury Estate &bull; Udachiwadi, Saswad</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


def send_inquiry_notification(inquiry):
    """
    Sends email notification to the villa owners/managers when a booking inquiry is submitted.
    Also sends confirmation email to the guest if their email is provided.
    Includes RFC 5546 multipart calendar invite (auto-recognized by Gmail & Apple Mail),
    Google Calendar API URL, Outlook URL, Yahoo URL, and direct device .ICS download link.
    """
    receivers = get_receiver_emails()
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Grace Ville <graceville1911@gmail.com>')
    
    # Generate multi-platform calendar links & RFC 5545 payload
    ics_content = generate_ics_invite(inquiry)
    gcal_url = get_google_calendar_url(inquiry)
    outlook_url = get_outlook_calendar_url(inquiry)
    yahoo_url = get_yahoo_calendar_url(inquiry)
    device_cal_url = get_device_calendar_url(inquiry)

    # 1. Email to Villa Management / Host
    subject = f"New Booking Inquiry: {inquiry.reference_id} - {inquiry.full_name} ({inquiry.get_stay_type_display()})"
    text_body = f"""Hello Grace Ville Team,

A new booking inquiry has been submitted on the Grace Ville website.

Reference ID:     {inquiry.reference_id}
Guest Name:       {inquiry.full_name}
Phone / WhatsApp: {inquiry.phone}
Email Address:    {inquiry.email or 'Not provided'}
Stay Package:     {inquiry.get_stay_type_display()}
Check-in Date:    {inquiry.check_in_date or 'Flexible / Not specified'}
Check-out Date:   {inquiry.check_out_date or 'Flexible / Not specified'}
Number of Guests: {inquiry.number_of_guests}
Special Requests: {inquiry.message or 'None'}

Submitted at:     {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Add to Google Calendar:  {gcal_url}
Add to Outlook Calendar: {outlook_url}
Download .ICS Calendar:  {device_cal_url}

Best regards,
Grace Ville Automated Booking System
Saswad, Udachiwadi, Pune
"""
    host_html = render_host_email_html(inquiry, gcal_url, outlook_url, device_cal_url)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=receivers,
        )
        msg.attach_alternative(host_html, "text/html")
        if ics_content:
            # Attach as alternative text/calendar part so Gmail & Apple Mail auto-detect the RSVP card
            msg.attach_alternative(ics_content, 'text/calendar; charset="utf-8"; method=REQUEST')
            # Also attach as downloadable file for Outlook desktop / manual download
            msg.attach(
                filename=f"graceville-{inquiry.reference_id}.ics",
                content=ics_content,
                mimetype='text/calendar; charset="utf-8"; method=REQUEST'
            )
        msg.send(fail_silently=False)
        logger.info(f"Booking inquiry email notification sent to {receivers} for {inquiry.reference_id}")
    except Exception as e:
        logger.error(f"Failed to send booking notification email to host: {e}")

    # 2. Confirmation Email to the Guest (if valid email provided)
    if inquiry.email and '@' in inquiry.email:
        guest_subject = f"Booking Inquiry Received - Grace Ville Villa (Ref: {inquiry.reference_id})"
        guest_text_body = f"""Dear {inquiry.full_name},

Thank you for choosing Grace Ville! We have received your booking inquiry and our reservation concierge will reach out to you shortly to confirm your dates and package.

YOUR INQUIRY SUMMARY:
Booking Reference: {inquiry.reference_id}
Package:           {inquiry.get_stay_type_display()}
Guests:            {inquiry.number_of_guests}
Check-in:          {inquiry.check_in_date or 'To be confirmed'}
Check-out:         {inquiry.check_out_date or 'Next Day 11:00 AM'}
Contact Phone:     {inquiry.phone}

ADD TO YOUR CALENDAR (FREE 1-TAP SYNC):
Google Calendar:  {gcal_url}
Apple / Device:   {device_cal_url}
Outlook Calendar: {outlook_url}
Yahoo Calendar:   {yahoo_url}

LOCATION & DIRECTIONS:
Grace Ville, Udachiwadi, Saswad, Pune, Maharashtra
Google Maps: https://maps.app.goo.gl/XPxZYJUyNyA1UPX79

WhatsApp Concierge:
https://wa.me/{getattr(settings, 'WHATSAPP_PHONE', '917768956163')}?text=Hi%20Grace%20Ville%20Team%2C%20inquiring%20about%20Ref%3A%20{inquiry.reference_id}

Warm regards,
The Grace Ville Team
Relax, Celebrate & Reconnect with Nature
"""
        guest_html = render_guest_email_html(inquiry, gcal_url, outlook_url, yahoo_url, device_cal_url)

        try:
            guest_msg = EmailMultiAlternatives(
                subject=guest_subject,
                body=guest_text_body,
                from_email=from_email,
                to=[inquiry.email],
            )
            guest_msg.attach_alternative(guest_html, "text/html")
            if ics_content:
                # Attach as alternative text/calendar part so Gmail & Apple Mail auto-detect the RSVP card
                guest_msg.attach_alternative(ics_content, 'text/calendar; charset="utf-8"; method=REQUEST')
                # Also attach as downloadable file for Outlook desktop / manual download
                guest_msg.attach(
                    filename=f"graceville-{inquiry.reference_id}.ics",
                    content=ics_content,
                    mimetype='text/calendar; charset="utf-8"; method=REQUEST'
                )
            guest_msg.send(fail_silently=True)
            logger.info(f"Guest confirmation email sent to {inquiry.email} for {inquiry.reference_id}")
        except Exception as e:
            logger.error(f"Failed to send guest confirmation email: {e}")


def send_contact_message_notification(contact_msg):
    """
    Sends email notification to the villa managers when a general contact message is sent.
    """
    receivers = get_receiver_emails()
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Grace Ville <graceville1911@gmail.com>')

    subject = f"Contact Message from {contact_msg.full_name}: {contact_msg.subject or 'General Inquiry'}"
    text_body = f"""Hello Grace Ville Team,

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
    html_body = render_contact_message_html(contact_msg)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=receivers,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Contact email sent to {receivers}")
    except Exception as e:
        logger.error(f"Failed to send contact notification email: {e}")
