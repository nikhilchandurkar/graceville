from django.conf import settings
import os
import urllib.parse

def whatsapp_context(request):
    """
    Context processor providing WhatsApp contact numbers and pre-built chat links across all templates.
    """
    primary_phone = getattr(settings, 'WHATSAPP_PHONE', '917768956163')
    owner_phone = os.environ.get('OWNER_PHONE', '919699825732')

    default_text = "Hi Grace Ville Concierge! I would like to inquire about booking the villa in Saswad."
    encoded_text = urllib.parse.quote(default_text)
    chat_url = f"https://wa.me/{primary_phone}?text={encoded_text}"
    owner_chat_url = f"https://wa.me/{owner_phone}?text={encoded_text}"

    contact_email = os.environ.get('CONTACT_EMAIL', getattr(settings, 'CONTACT_EMAIL', 'graceville1911@gmail.com'))

    return {
        'WHATSAPP_PHONE': primary_phone,
        'WHATSAPP_PHONE_FORMATTED': '+91 77689 56163',
        'OWNER_PHONE': owner_phone,
        'OWNER_PHONE_FORMATTED': '+91 96998 25732',
        'CONTACT_EMAIL': contact_email,
        'WHATSAPP_CHAT_URL': chat_url,
        'OWNER_CHAT_URL': owner_chat_url,
    }
