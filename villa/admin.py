from django.contrib import admin
from django.utils.html import format_html
from .models import BookingInquiry, ContactMessage, VillaSpace

@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id',
        'full_name',
        'phone',
        'email',
        'stay_type_badge',
        'number_of_guests',
        'status_badge',
        'created_at',
    )
    list_filter = ('status', 'stay_type', 'created_at')
    search_fields = ('reference_id', 'full_name', 'email', 'phone', 'message')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
    list_per_page = 20
    actions = ['mark_as_contacted', 'mark_as_confirmed', 'mark_as_cancelled']

    def stay_type_badge(self, obj):
        color = "#17a2b8" if obj.stay_type == "overnight" else "#28a745" if obj.stay_type == "day_outing" else "#fd7e14"
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600;">{}</span>',
            color,
            obj.get_stay_type_display()
        )
    stay_type_badge.short_description = "Package Type"

    def status_badge(self, obj):
        colors = {
            'new': '#f35525',
            'contacted': '#ffc107',
            'confirmed': '#28a745',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        text_color = '#000' if obj.status == 'contacted' else '#fff'
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:bold;">{}</span>',
            color,
            text_color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    @admin.action(description="Mark selected as Contacted")
    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted')

    @admin.action(description="Mark selected as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description="Mark selected as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read']

    @admin.action(description="Mark selected messages as Read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(VillaSpace)
class VillaSpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'subtitle', 'order', 'is_active')
    list_display_links = ('id', 'title')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'subtitle', 'spec_1', 'spec_2')
