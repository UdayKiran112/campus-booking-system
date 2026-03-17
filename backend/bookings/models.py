from django.db import models
from django.utils import timezone
from datetime import timedelta
from users.models import User
from venues.models import Venue


class Booking(models.Model):
    """Main booking model"""

    class BookingStatus(models.TextChoices):
        PRE_BOOKED = "PRE_BOOKED", "Pre-Booked (Pending Payment)"
        PENDING_APPROVAL = "PENDING_APPROVAL", "Pending Approval"
        APPROVED = "APPROVED", "Approved"
        CONFIRMED = "CONFIRMED", "Confirmed"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"
        NO_SHOW = "NO_SHOW", "No Show"

    class PriorityLevel(models.IntegerChoices):
        P1_EXAM = 1, "Exam/University Event"
        P2_ACADEMIC = 2, "Academic Event"
        P3_DEPARTMENT = 3, "Department/School Meet"
        P4_CLUB = 4, "Club/Cultural Event"
        P5_PERSONAL = 5, "Personal/Informal Use"

    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="bookings")

    # Booking Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)

    # Priority and Status
    priority = models.IntegerField(
        choices=PriorityLevel.choices, default=PriorityLevel.P5_PERSONAL
    )
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.PRE_BOOKED
    )

    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_bookings",
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # Payment
    payment_required = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=20, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default="PENDING")
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    # Deposit
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_refunded = models.BooleanField(default=False)
    refund_date = models.DateTimeField(null=True, blank=True)

    # Check-in/Check-out
    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    checked_out = models.BooleanField(default=False)
    check_out_time = models.DateTimeField(null=True, blank=True)

    # Metadata
    booking_reference = models.CharField(max_length=50, unique=True)
    invoice_generated = models.BooleanField(default=False)
    invoice_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookings"
        ordering = ["-booking_date", "-start_time"]
        indexes = [
            models.Index(fields=["venue", "booking_date"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["booking_reference"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.venue.name} on {self.booking_date}"

    def save(self, *args, **kwargs):
        # Generate booking reference if not exists
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()

        # Calculate duration
        if self.start_time and self.end_time:
            start_datetime = timezone.datetime.combine(
                timezone.now().date(), self.start_time
            )
            end_datetime = timezone.datetime.combine(
                timezone.now().date(), self.end_time
            )
            duration = (end_datetime - start_datetime).total_seconds() / 3600
            self.duration_hours = duration

        super().save(*args, **kwargs)

    def generate_booking_reference(self):
        """Generate unique booking reference"""
        import random
        import string

        prefix = self.venue.category[:3].upper()
        random_str = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        return f"{prefix}-{random_str}"

    def is_conflicting(self):
        """Check if this booking conflicts with existing bookings"""
        conflicts = Booking.objects.filter(
            venue=self.venue,
            booking_date=self.booking_date,
            status__in=[
                self.BookingStatus.CONFIRMED,
                self.BookingStatus.APPROVED,
                self.BookingStatus.PENDING_APPROVAL,
            ],
        ).exclude(id=self.id)

        for booking in conflicts:
            # Check time overlap
            if (
                self.start_time < booking.end_time
                and self.end_time > booking.start_time
            ):
                return True, booking

        return False, None

    def can_displace(self, existing_booking):
        """Check if this booking can displace an existing booking"""
        return self.priority < existing_booking.priority

    @property
    def is_past(self):
        """Check if booking date has passed"""
        booking_datetime = timezone.datetime.combine(self.booking_date, self.end_time)
        return booking_datetime < timezone.now()

    @property
    def should_mark_no_show(self):
        """Check if booking should be marked as no-show"""
        if self.checked_in:
            return False

        booking_datetime = timezone.datetime.combine(self.booking_date, self.start_time)
        no_show_threshold = booking_datetime + timedelta(minutes=15)

        return timezone.now() > no_show_threshold


class ConflictResolution(models.Model):
    """Track booking conflict resolutions"""

    original_booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="original_conflicts"
    )
    new_booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="new_conflicts"
    )

    conflict_detected_at = models.DateTimeField(auto_now_add=True)
    resolution_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending User Response"),
            ("ACCEPTED", "Original User Accepted Alternative"),
            ("DROPPED", "Original User Dropped Booking"),
            ("EXPIRED", "Response Window Expired"),
        ],
        default="PENDING",
    )

    alternative_slots_offered = models.JSONField(default=list)
    user_response_deadline = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "conflict_resolutions"
        ordering = ["-conflict_detected_at"]

    def __str__(self):
        return f"Conflict: {self.original_booking.booking_reference} vs {self.new_booking.booking_reference}"


class BookingModification(models.Model):
    """Track all modifications to bookings"""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="modifications"
    )
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    old_date = models.DateField(null=True, blank=True)
    new_date = models.DateField(null=True, blank=True)
    old_start_time = models.TimeField(null=True, blank=True)
    new_start_time = models.TimeField(null=True, blank=True)
    old_end_time = models.TimeField(null=True, blank=True)
    new_end_time = models.TimeField(null=True, blank=True)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)

    reason = models.TextField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking_modifications"
        ordering = ["-modified_at"]

    def __str__(self):
        return f"Modification to {self.booking.booking_reference} at {self.modified_at}"


class Invoice(models.Model):
    """Store invoice information"""

    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="invoice"
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateTimeField(auto_now_add=True)

    # Charges
    venue_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # PDF
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-invoice_date"]

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.booking.booking_reference}"

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import random
        import string

        date_str = timezone.now().strftime("%Y%m%d")
        random_str = "".join(random.choices(string.digits, k=6))
        return f"INV-{date_str}-{random_str}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
