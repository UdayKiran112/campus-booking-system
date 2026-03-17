from rest_framework import serializers
from django.utils import timezone
from .models import Booking, ConflictResolution, BookingModification, Invoice
from venues.serializers import VenueSerializer
from users.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    venue_details = VenueSerializer(source="venue", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    approved_by_details = UserSerializer(source="approved_by", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    is_past = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "user_details",
            "venue",
            "venue_details",
            "title",
            "description",
            "booking_date",
            "start_time",
            "end_time",
            "duration_hours",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "approved_by",
            "approved_by_details",
            "approval_date",
            "rejection_reason",
            "payment_required",
            "payment_amount",
            "payment_type",
            "payment_status",
            "payment_id",
            "security_deposit",
            "deposit_refunded",
            "checked_in",
            "check_in_time",
            "checked_out",
            "check_out_time",
            "booking_reference",
            "invoice_generated",
            "invoice_sent",
            "is_past",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "duration_hours",
            "approved_by",
            "approval_date",
            "payment_id",
            "payment_date",
            "deposit_refunded",
            "refund_date",
            "booking_reference",
            "created_at",
            "updated_at",
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "venue",
            "title",
            "description",
            "booking_date",
            "start_time",
            "end_time",
            "priority",
        ]

    def validate(self, data):
        # Validate date is in future
        if data["booking_date"] < timezone.now().date():
            raise serializers.ValidationError("Cannot book dates in the past")

        # Validate time range
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("End time must be after start time")

        # Validate venue operating hours
        venue = data["venue"]
        if data["start_time"] < venue.available_from:
            raise serializers.ValidationError(f"Venue opens at {venue.available_from}")
        if data["end_time"] > venue.available_to:
            raise serializers.ValidationError(f"Venue closes at {venue.available_to}")

        return data

    def create(self, validated_data):
        # Set user from context
        validated_data["user"] = self.context["request"].user

        # Calculate pricing
        venue = validated_data["venue"]
        user = validated_data["user"]
        pricing = venue.get_pricing_for_user(user)

        validated_data["payment_type"] = pricing["payment_type"]
        validated_data["payment_amount"] = pricing["base_price"]
        validated_data["security_deposit"] = pricing["security_deposit"]
        validated_data["payment_required"] = (
            pricing["base_price"] > 0 or pricing["security_deposit"] > 0
        )

        # Set initial status
        if validated_data["payment_required"]:
            validated_data["status"] = Booking.BookingStatus.PRE_BOOKED
        else:
            validated_data["status"] = Booking.BookingStatus.PENDING_APPROVAL

        return super().create(validated_data)


class ConflictResolutionSerializer(serializers.ModelSerializer):
    original_booking_details = BookingSerializer(
        source="original_booking", read_only=True
    )
    new_booking_details = BookingSerializer(source="new_booking", read_only=True)

    class Meta:
        model = ConflictResolution
        fields = [
            "id",
            "original_booking",
            "original_booking_details",
            "new_booking",
            "new_booking_details",
            "conflict_detected_at",
            "resolution_status",
            "alternative_slots_offered",
            "user_response_deadline",
            "resolved_at",
        ]


class BookingModificationSerializer(serializers.ModelSerializer):
    modified_by_details = UserSerializer(source="modified_by", read_only=True)

    class Meta:
        model = BookingModification
        fields = [
            "id",
            "booking",
            "modified_by",
            "modified_by_details",
            "old_date",
            "new_date",
            "old_start_time",
            "new_start_time",
            "old_end_time",
            "new_end_time",
            "old_status",
            "new_status",
            "reason",
            "modified_at",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    booking_details = BookingSerializer(source="booking", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "booking",
            "booking_details",
            "invoice_number",
            "invoice_date",
            "venue_charge",
            "security_deposit",
            "tax_amount",
            "total_amount",
            "pdf_file",
        ]


class SlotAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking slot availability"""

    venue_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class AlternativeSlotSerializer(serializers.Serializer):
    """Serializer for alternative slot suggestions"""

    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    is_available = serializers.BooleanField()
