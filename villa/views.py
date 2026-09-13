import urllib.parse
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from .models import BookingInquiry, ContactMessage, VillaSpace
from .forms import BookingInquiryForm, ContactMessageForm
from .emails import send_inquiry_notification, send_contact_message_notification
from .storage import store_booking_in_mongo, store_contact_in_mongo

logger = logging.getLogger(__name__)

DEFAULT_SPACES = [
    {
        'title': 'Udachiwadi, Saswad Estate',
        'subtitle': '33 km from Pune',
        'category': 'outdoor',
        'location_info': 'Near Purandar Airport',
        'spec_1': 'Bedrooms: 3 AC + 1 AC Dorm',
        'spec_2': 'Washrooms: 5',
        'spec_3': 'Kitchens: 3',
        'spec_4': 'Setting: Mountain Foothills',
        'spec_5': 'Parking: Ample Private',
        'image_rel_path': 'assets/images/property-01.jpg',
    },
    {
        'title': 'Waterfall Swimming Pool',
        'subtitle': 'Private Oasis',
        'category': 'outdoor',
        'location_info': 'Grace Ville Poolside Deck',
        'spec_1': 'Pool: Private Waterfall Pool',
        'spec_2': 'Feature: Cascading Stone Fall',
        'spec_3': 'Deck: Slate Paved & Gazebo',
        'spec_4': 'Ambiance: Mountain Backdrop',
        'spec_5': 'Events: Day Outing & Parties',
        'image_rel_path': 'assets/images/property-02.jpg',
    },
    {
        'title': 'Living & Dining Grand Hall',
        'subtitle': 'Grand Living Lounge',
        'category': 'indoor',
        'location_info': 'Ground Floor Main Lounge',
        'spec_1': 'Sofas: Plush Leather Lounges',
        'spec_2': 'Dining: 6-Seater Marble Table',
        'spec_3': 'Audio: JBL Music System',
        'spec_4': 'Flooring: Polished Marble Tiles',
        'spec_5': 'Lighting: Designer Wall Sconces',
        'image_rel_path': 'assets/images/property-03.jpg',
    },
    {
        'title': 'Scenic Mountain View Suite',
        'subtitle': 'Balcony Suite',
        'category': 'bedrooms',
        'location_info': 'Upper Floor Mountain Wing',
        'spec_1': 'Air Conditioning: Yes (AC)',
        'spec_2': 'Balcony: Direct Glass Walkout',
        'spec_3': 'View: Purandar Valley & Hills',
        'spec_4': 'Washroom: Attached Designer Bath',
        'spec_5': 'Bed: King Size Luxury Bed',
        'image_rel_path': 'assets/images/property-04.jpg',
    },
    {
        'title': 'Fully-Equipped Modular Kitchen',
        'subtitle': '3 Kitchens Available',
        'category': 'indoor',
        'location_info': 'Main & Prep Kitchens',
        'spec_1': 'Total Kitchens: 3 Kitchens',
        'spec_2': 'Cooktop: Multi-Burner Gas Stove',
        'spec_3': 'Appliances: Refrigerator & Cookware',
        'spec_4': 'Prep Area: Modern Granite Slabs',
        'spec_5': 'Service: Ideal for Group Meals',
        'image_rel_path': 'assets/images/property-05.jpg',
    },
    {
        'title': 'Covered Timber Sky Sitout',
        'subtitle': '360° Mountain Vistas',
        'category': 'terrace',
        'location_info': 'Rooftop & 1st Floor Terrace',
        'spec_1': 'Ceiling: Polished Timber Wood',
        'spec_2': '360° View: Hills & Sunset Horizon',
        'spec_3': 'Night Vibe: Lantern Balustrades',
        'spec_4': 'Activities: Nature Walks & Trekking',
        'spec_5': 'Orchard: Mangoes & Jambu Trees',
        'image_rel_path': 'assets/images/property-06.jpg',
    },
]

def get_villa_spaces():
    try:
        spaces = list(VillaSpace.objects.filter(is_active=True))
        if spaces:
            return spaces
    except Exception as e:
        logger.error(f"Error querying VillaSpace: {e}")
    return DEFAULT_SPACES

def sync_inquiry_everywhere(inquiry):
    """
    Helper function to dispatch SMTP notification email and persist to MongoDB Atlas.
    """
    # 1. Send SMTP Notification Email to configured receivers + confirmation to guest
    try:
        send_inquiry_notification(inquiry)
    except Exception as e:
        logger.error(f"SMTP notification error: {e}")

    # 2. Persist to MongoDB Atlas if MONGODB_URI is configured
    try:
        store_booking_in_mongo({
            'reference_id': inquiry.reference_id,
            'full_name': inquiry.full_name,
            'email': inquiry.email,
            'phone': inquiry.phone,
            'stay_type': inquiry.stay_type,
            'stay_type_display': inquiry.get_stay_type_display(),
            'check_in_date': str(inquiry.check_in_date) if inquiry.check_in_date else None,
            'check_out_date': str(inquiry.check_out_date) if inquiry.check_out_date else None,
            'number_of_guests': inquiry.number_of_guests,
            'message': inquiry.message,
            'status': inquiry.status,
            'created_at': inquiry.created_at.isoformat() if hasattr(inquiry, 'created_at') and inquiry.created_at else None,
        })
    except Exception as e:
        logger.error(f"MongoDB Atlas sync error: {e}")

def sync_contact_everywhere(contact_msg):
    """
    Helper function to dispatch SMTP notification and persist contact to MongoDB Atlas.
    """
    try:
        send_contact_message_notification(contact_msg)
    except Exception as e:
        logger.error(f"SMTP contact email error: {e}")

    try:
        store_contact_in_mongo({
            'full_name': contact_msg.full_name,
            'email': contact_msg.email,
            'phone': contact_msg.phone,
            'subject': contact_msg.subject,
            'message': contact_msg.message,
            'created_at': contact_msg.created_at.isoformat() if hasattr(contact_msg, 'created_at') and contact_msg.created_at else None,
        })
    except Exception as e:
        logger.error(f"MongoDB Atlas contact sync error: {e}")

def index(request):
    spaces = get_villa_spaces()
    booking_form = BookingInquiryForm()
    
    if request.method == 'POST':
        booking_form = BookingInquiryForm(request.POST)
        if booking_form.is_valid():
            inquiry = booking_form.save()
            sync_inquiry_everywhere(inquiry)
            messages.success(request, f"Thank you, {inquiry.full_name}! Your booking inquiry ({inquiry.reference_id}) has been recorded. Our concierge will contact you shortly.")
            return redirect('index')

    context = {
        'spaces': spaces,
        'booking_form': booking_form,
        'active_page': 'home',
    }
    return render(request, 'index.html', context)

def properties(request):
    spaces = get_villa_spaces()
    context = {
        'spaces': spaces,
        'active_page': 'properties',
    }
    return render(request, 'properties.html', context)

def property_details(request):
    spaces = get_villa_spaces()
    context = {
        'spaces': spaces,
        'active_page': 'property_details',
    }
    return render(request, 'property_details.html', context)

def contact(request):
    contact_form = ContactMessageForm()
    booking_form = BookingInquiryForm()

    if request.method == 'POST':
        if 'stay_type' in request.POST:
            booking_form = BookingInquiryForm(request.POST)
            if booking_form.is_valid():
                inquiry = booking_form.save()
                sync_inquiry_everywhere(inquiry)
                messages.success(request, f"Inquiry received! Reference: {inquiry.reference_id}. Our team will contact you soon.")
                return redirect('contact')
        else:
            contact_form = ContactMessageForm(request.POST)
            if contact_form.is_valid():
                contact_msg = contact_form.save()
                sync_contact_everywhere(contact_msg)
                messages.success(request, "Thank you! Your message has been sent to Grace Ville management.")
                return redirect('contact')

    context = {
        'contact_form': contact_form,
        'booking_form': booking_form,
        'active_page': 'contact',
    }
    return render(request, 'contact.html', context)

@require_POST
def api_book(request):
    """
    AJAX endpoint for instant booking inquiry submission.
    Saves to database, dispatches SMTP email, syncs to MongoDB Atlas, and returns WhatsApp link.
    """
    import re
    from datetime import datetime
    from django.utils import timezone
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    full_name = (request.POST.get('name') or request.POST.get('full_name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    stay_type = request.POST.get('stay_type', 'overnight')
    raw_date = (request.POST.get('date') or request.POST.get('visit_date') or request.POST.get('check_in_date') or '').strip()
    time_slot = (request.POST.get('time_slot') or '').strip()
    raw_guests = request.POST.get('guests') or request.POST.get('number_of_guests') or 6
    message = (request.POST.get('message') or '').strip()

    # 1. Name validation
    if not full_name or len(full_name) < 2:
        return JsonResponse({
            'status': 'error',
            'error': 'Please enter a valid full name (minimum 2 characters).'
        }, status=400)

    # 2. Phone validation
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) < 10:
        return JsonResponse({
            'status': 'error',
            'error': 'Please enter a valid 10-digit phone or WhatsApp number.'
        }, status=400)

    # 3. Email validation (if provided)
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'status': 'error',
                'error': 'Please enter a valid email address.'
            }, status=400)

    # 4. Date validation (must not be in the past)
    parsed_date = None
    if not raw_date:
        return JsonResponse({
            'status': 'error',
            'error': 'Please select your preferred date.'
        }, status=400)

    try:
        parsed_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
        today = timezone.now().date()
        if parsed_date < today:
            return JsonResponse({
                'status': 'error',
                'error': f'Booking date cannot be in the past ({parsed_date.strftime("%d-%m-%Y")}). Please choose today or a future date.'
            }, status=400)
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'error': 'Invalid date format. Please choose a valid date from the calendar.'
        }, status=400)

    # 5. Guests validation
    try:
        num_guests = int(raw_guests)
        if num_guests < 1 or num_guests > 60:
            return JsonResponse({
                'status': 'error',
                'error': 'Estimated number of guests must be between 1 and 60.'
            }, status=400)
    except (ValueError, TypeError):
        num_guests = 6

    # Normalize stay_type (support visit/inspection appointment)
    if 'visit' in stay_type.lower() or 'inspect' in stay_type.lower() or 'appoint' in stay_type.lower():
        norm_stay = 'visit'
    elif 'day' in stay_type.lower():
        norm_stay = 'day_outing'
    elif 'celebrat' in stay_type.lower() or 'event' in stay_type.lower():
        norm_stay = 'celebration'
    else:
        norm_stay = 'overnight'

    notes_parts = []
    if time_slot:
        notes_parts.append(f"Preferred Slot: {time_slot}")
    if message:
        notes_parts.append(message)
    combined_notes = " | ".join(notes_parts)

    inquiry = BookingInquiry.objects.create(
        full_name=full_name,
        email=email,
        phone=phone,
        stay_type=norm_stay,
        check_in_date=parsed_date,
        number_of_guests=num_guests,
        message=combined_notes
    )

    # Sync everywhere (SMTP Email + MongoDB Atlas)
    sync_inquiry_everywhere(inquiry)

    # Format WhatsApp URL with configured phone (clean, natural professional text)
    wa_phone = getattr(settings, 'WHATSAPP_PHONE', '917768956163')
    wa_lines = [
        "Hello Grace Ville Concierge,",
        "I would like to inquire about booking Grace Ville.",
        "----------------------------------------",
        f"Booking Reference: {inquiry.reference_id}",
        f"Name: {full_name}",
        f"Phone: {phone}",
        f"Stay Type: {inquiry.get_stay_type_display()}",
    ]
    if inquiry.check_in_date:
        wa_lines.append(f"Preferred Date: {inquiry.check_in_date.strftime('%d-%m-%Y')}")
    if time_slot:
        wa_lines.append(f"Preferred Slot: {time_slot}")
    if num_guests:
        wa_lines.append(f"Estimated Guests: {num_guests}")
    if message:
        wa_lines.append(f"Notes: {message}")
    wa_lines.append("----------------------------------------")
    wa_lines.append("Please confirm availability.")
    wa_text = "\n".join(wa_lines)
    wa_encoded = urllib.parse.quote(wa_text)
    wa_url = f"https://wa.me/{wa_phone}?text={wa_encoded}"

    return JsonResponse({
        'status': 'success',
        'reference_id': inquiry.reference_id,
        'message': f"Inquiry registered successfully. Reference: {inquiry.reference_id}.",
        'whatsapp_url': wa_url
    })

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)
