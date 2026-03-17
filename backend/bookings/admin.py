from django.contrib import admin
from .models import Booking, ConflictResolution, BookingModification, Invoice


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'venue', 'booking_date', 'start_time', 
                    'status', 'priority', 'payment_status']
    list_filter = ['status', 'priority', 'payment_status', 'booking_date', 'checked_in']
    search_fields = ['booking_reference', 'user__username', 'venue__name', 'title']
    date_hierarchy = 'booking_date'
    readonly_fields = ['booking_reference', 'duration_hours', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'venue', 'title', 'description', 'booking_reference')
        }),
        ('Date & Time', {
            'fields': ('booking_date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Priority & Status', {
            'fields': ('priority', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date', 'rejection_reason')
        }),
        ('Payment', {
            'fields': ('payment_required', 'payment_amount', 'payment_type', 
                      'payment_status', 'payment_id', 'payment_date',
                      'security_deposit', 'deposit_refunded', 'refund_date')
        }),
        ('Check-in/Check-out', {
            'fields': ('checked_in', 'check_in_time', 'checked_out', 'check_out_time')
        }),
        ('Invoice', {
            'fields': ('invoice_generated', 'invoice_sent')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ConflictResolution)
class ConflictResolutionAdmin(admin.ModelAdmin):
    list_display = ['original_booking', 'new_booking', 'resolution_status', 
                    'conflict_detected_at', 'user_response_deadline']
    list_filter = ['resolution_status', 'conflict_detected_at']
    search_fields = ['original_booking__booking_reference', 'new_booking__booking_reference']
    date_hierarchy = 'conflict_detected_at'


@admin.register(BookingModification)
class BookingModificationAdmin(admin.ModelAdmin):
    list_display = ['booking', 'modified_by', 'old_status', 'new_status', 'modified_at']
    list_filter = ['old_status', 'new_status', 'modified_at']
    search_fields = ['booking__booking_reference', 'modified_by__username', 'reason']
    date_hierarchy = 'modified_at'
    readonly_fields = ['modified_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'total_amount', 'invoice_date']
    search_fields = ['invoice_number', 'booking__booking_reference']
    readonly_fields = ['invoice_number', 'invoice_date']
    date_hierarchy = 'invoice_date'
