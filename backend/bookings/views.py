from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking, ConflictResolution, BookingModification, Invoice
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    ConflictResolutionSerializer,
    InvoiceSerializer,
    SlotAvailabilitySerializer,
    AlternativeSlotSerializer,
)
from venues.models import Venue
from users.models import User


class BookingListView(generics.ListAPIView):
    """List bookings with filtering"""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.all()

        # Filter based on user role
        if not user.is_authority:
            # Regular users see only their bookings
            queryset = queryset.filter(user=user)
        else:
            # Authorities see bookings for their venues
            controlled_venues = Venue.objects.filter(
                Q(controlling_authority=user) | Q(department=user.department)
            )
            queryset = queryset.filter(Q(user=user) | Q(venue__in=controlled_venues))

        # Apply filters
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        venue_id = self.request.query_params.get("venue")
        if venue_id:
            queryset = queryset.filter(venue_id=venue_id)

        date_from = self.request.query_params.get("date_from")
        if date_from:
            queryset = queryset.filter(booking_date__gte=date_from)

        date_to = self.request.query_params.get("date_to")
        if date_to:
            queryset = queryset.filter(booking_date__lte=date_to)

        return queryset


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details"""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.all()

        if not user.is_authority:
            queryset = queryset.filter(user=user)

        return queryset


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking (pre-booking)"""

    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check slot availability
        venue_id = serializer.validated_data["venue"].id
        booking_date = serializer.validated_data["booking_date"]
        start_time = serializer.validated_data["start_time"]
        end_time = serializer.validated_data["end_time"]

        availability_response = check_slot_availability(
            venue_id, booking_date, start_time, end_time
        )

        if not availability_response["is_available"]:
            # Slot is not available - check for conflict resolution
            conflicting_booking = availability_response.get("conflicting_booking")

            if conflicting_booking:
                return Response(
                    {
                        "available": False,
                        "conflict": True,
                        "message": "Slot is already booked",
                        "conflicting_booking": BookingSerializer(
                            conflicting_booking
                        ).data,
                        "can_request_review": True,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                {
                    "available": False,
                    "conflict": False,
                    "message": availability_response.get(
                        "reason", "Slot is not available"
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Slot is available - create pre-booking
        booking = serializer.save()

        return Response(
            {
                "message": "Pre-booking created successfully",
                "booking": BookingSerializer(booking).data,
                "payment_required": booking.payment_required,
                "payment_details": {
                    "amount": float(booking.payment_amount),
                    "security_deposit": float(booking.security_deposit),
                    "payment_type": booking.payment_type,
                    "total": float(booking.payment_amount + booking.security_deposit),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_availability_view(request):
    """Check if a slot is available"""
    serializer = SlotAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    venue_id = serializer.validated_data["venue_id"]
    booking_date = serializer.validated_data["date"]
    start_time = serializer.validated_data["start_time"]
    end_time = serializer.validated_data["end_time"]

    result = check_slot_availability(venue_id, booking_date, start_time, end_time)

    return Response(result)


def check_slot_availability(venue_id, booking_date, start_time, end_time):
    """Helper function to check slot availability"""
    try:
        venue = Venue.objects.get(id=venue_id, is_active=True)
    except Venue.DoesNotExist:
        return {"is_available": False, "reason": "Venue not found or inactive"}

    # Check if date is in the past
    if booking_date < timezone.now().date():
        return {"is_available": False, "reason": "Cannot book dates in the past"}

    # Check venue operating hours
    if start_time < venue.available_from or end_time > venue.available_to:
        return {
            "is_available": False,
            "reason": f"Venue operates from {venue.available_from} to {venue.available_to}",
        }

    # Check for special availability rules
    from venues.models import VenueAvailability

    special_availability = VenueAvailability.objects.filter(
        venue=venue, date=booking_date
    ).first()

    if special_availability and not special_availability.is_available:
        return {
            "is_available": False,
            "reason": special_availability.reason or "Venue is blocked for this date",
        }

    # Check for conflicting bookings
    conflicting_bookings = Booking.objects.filter(
        venue=venue,
        booking_date=booking_date,
        status__in=[
            Booking.BookingStatus.CONFIRMED,
            Booking.BookingStatus.APPROVED,
            Booking.BookingStatus.PENDING_APPROVAL,
            Booking.BookingStatus.PRE_BOOKED,
        ],
    )

    for booking in conflicting_bookings:
        # Check time overlap
        if start_time < booking.end_time and end_time > booking.start_time:
            return {
                "is_available": False,
                "conflicting_booking": booking,
                "reason": f"Slot conflicts with existing booking: {booking.booking_reference}",
            }

    return {"is_available": True, "venue": venue}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_alternative_slots_view(request, venue_id):
    """Get alternative available slots for a venue"""
    date_str = request.query_params.get("date")
    duration_str = request.query_params.get("duration", "2")  # Default 2 hours

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        duration_hours = float(duration_str)
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid date or duration format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        venue = Venue.objects.get(id=venue_id, is_active=True)
    except Venue.DoesNotExist:
        return Response({"error": "Venue not found"}, status=status.HTTP_404_NOT_FOUND)

    # Generate alternative slots
    alternative_slots = []

    # Check for 7 days from target date
    for day_offset in range(7):
        check_date = target_date + timedelta(days=day_offset)

        # Generate time slots (every hour)
        current_time = venue.available_from
        end_of_day = venue.available_to

        while True:
            # Calculate slot end time
            slot_start = current_time
            slot_end_dt = datetime.combine(check_date, current_time) + timedelta(
                hours=duration_hours
            )
            slot_end = slot_end_dt.time()

            if slot_end > end_of_day:
                break

            # Check availability
            availability = check_slot_availability(
                venue_id, check_date, slot_start, slot_end
            )

            alternative_slots.append(
                {
                    "date": check_date,
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "is_available": availability["is_available"],
                }
            )

            # Move to next hour
            next_hour = datetime.combine(check_date, current_time) + timedelta(hours=1)
            current_time = next_hour.time()

            if current_time >= end_of_day:
                break

    # Filter only available slots
    available_slots = [slot for slot in alternative_slots if slot["is_available"]]

    return Response(
        {
            "venue_id": venue_id,
            "venue_name": venue.name,
            "requested_date": target_date,
            "duration_hours": duration_hours,
            "available_slots": available_slots[:20],  # Return first 20 slots
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_booking_view(request, pk):
    """Approve a booking (authority only)"""
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if user can approve this booking
    if not booking.venue.can_user_approve(request.user):
        return Response(
            {"error": "You do not have permission to approve this booking"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if booking.status != Booking.BookingStatus.PENDING_APPROVAL:
        return Response(
            {"error": "Booking is not in pending approval status"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update booking status
    old_status = booking.status
    booking.status = Booking.BookingStatus.APPROVED
    booking.approved_by = request.user
    booking.approval_date = timezone.now()
    booking.save()

    # Track modification
    BookingModification.objects.create(
        booking=booking,
        modified_by=request.user,
        old_status=old_status,
        new_status=booking.status,
        reason="Booking approved",
    )

    # TODO: Send email notification

    return Response(
        {
            "message": "Booking approved successfully",
            "booking": BookingSerializer(booking).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_booking_view(request, pk):
    """Reject a booking (authority only)"""
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if user can reject this booking
    if not booking.venue.can_user_approve(request.user):
        return Response(
            {"error": "You do not have permission to reject this booking"},
            status=status.HTTP_403_FORBIDDEN,
        )

    rejection_reason = request.data.get("reason", "")

    # Update booking status
    old_status = booking.status
    booking.status = Booking.BookingStatus.REJECTED
    booking.rejection_reason = rejection_reason
    booking.save()

    # Track modification
    BookingModification.objects.create(
        booking=booking,
        modified_by=request.user,
        old_status=old_status,
        new_status=booking.status,
        reason=f"Booking rejected: {rejection_reason}",
    )

    # TODO: Send email notification

    return Response(
        {"message": "Booking rejected", "booking": BookingSerializer(booking).data}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_payment_view(request, pk):
    """Confirm payment for a booking"""
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if booking.status != Booking.BookingStatus.PRE_BOOKED:
        return Response(
            {"error": "Booking is not in pre-booked status"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment_id = request.data.get("payment_id")

    # Update payment status
    booking.payment_status = "COMPLETED"
    booking.payment_id = payment_id
    booking.payment_date = timezone.now()
    booking.status = Booking.BookingStatus.PENDING_APPROVAL
    booking.save()

    # TODO: Verify payment with Razorpay

    return Response(
        {
            "message": "Payment confirmed. Booking sent for approval.",
            "booking": BookingSerializer(booking).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_booking_view(request, pk):
    """Cancel a booking"""
    try:
        booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if booking.status in [
        Booking.BookingStatus.COMPLETED,
        Booking.BookingStatus.CANCELLED,
    ]:
        return Response(
            {"error": "Cannot cancel this booking"}, status=status.HTTP_400_BAD_REQUEST
        )

    reason = request.data.get("reason", "")

    # Update booking status
    old_status = booking.status
    booking.status = Booking.BookingStatus.CANCELLED
    booking.save()

    # Track modification
    BookingModification.objects.create(
        booking=booking,
        modified_by=request.user,
        old_status=old_status,
        new_status=booking.status,
        reason=f"Cancelled by user: {reason}",
    )

    # TODO: Process refund if applicable

    return Response(
        {
            "message": "Booking cancelled successfully",
            "booking": BookingSerializer(booking).data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_review_view(request, pk):
    """Request review for a conflicting booking"""
    try:
        new_booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Check for conflicts
    is_conflicting, conflicting_booking = new_booking.is_conflicting()

    if not is_conflicting:
        return Response(
            {"error": "No conflict detected"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Check if new booking has higher priority
    if not new_booking.can_displace(conflicting_booking):
        return Response(
            {
                "error": "Your booking does not have sufficient priority to displace the existing booking",
                "conflicting_booking": BookingSerializer(conflicting_booking).data,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Create conflict resolution
    conflict = ConflictResolution.objects.create(
        original_booking=conflicting_booking,
        new_booking=new_booking,
        user_response_deadline=timezone.now() + timedelta(hours=24),
    )

    # Get alternative slots
    alternative_slots = get_alternative_slots_for_booking(conflicting_booking)
    conflict.alternative_slots_offered = alternative_slots
    conflict.save()

    # TODO: Send notification to original booking user

    return Response(
        {
            "message": "Review request submitted. Original user will be notified.",
            "conflict": ConflictResolutionSerializer(conflict).data,
        },
        status=status.HTTP_201_CREATED,
    )


def get_alternative_slots_for_booking(booking):
    """Helper to get alternative slots for a booking"""
    venue = booking.venue
    duration_hours = float(booking.duration_hours)

    alternative_slots = []

    # Check for 7 days from booking date
    for day_offset in range(7):
        check_date = booking.booking_date + timedelta(days=day_offset)

        # Skip the original date
        if check_date == booking.booking_date:
            continue

        # Generate time slots
        current_time = venue.available_from

        while True:
            slot_start = current_time
            slot_end_dt = datetime.combine(check_date, current_time) + timedelta(
                hours=duration_hours
            )
            slot_end = slot_end_dt.time()

            if slot_end > venue.available_to:
                break

            # Check availability
            availability = check_slot_availability(
                venue.id, check_date, slot_start, slot_end
            )

            if availability["is_available"]:
                alternative_slots.append(
                    {
                        "date": check_date.isoformat(),
                        "start_time": slot_start.isoformat(),
                        "end_time": slot_end.isoformat(),
                    }
                )

                if len(alternative_slots) >= 10:
                    return alternative_slots

            # Move to next hour
            next_hour = datetime.combine(check_date, current_time) + timedelta(hours=1)
            current_time = next_hour.time()

    return alternative_slots
