from django.urls import path
from . import views

urlpatterns = [
    path("", views.BookingListView.as_view(), name="booking-list"),
    path("<int:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("create/", views.BookingCreateView.as_view(), name="booking-create"),
    path(
        "check-availability/", views.check_availability_view, name="check-availability"
    ),
    path(
        "alternative-slots/<int:venue_id>/",
        views.get_alternative_slots_view,
        name="alternative-slots",
    ),
    path("<int:pk>/approve/", views.approve_booking_view, name="booking-approve"),
    path("<int:pk>/reject/", views.reject_booking_view, name="booking-reject"),
    path(
        "<int:pk>/confirm-payment/", views.confirm_payment_view, name="confirm-payment"
    ),
    path("<int:pk>/cancel/", views.cancel_booking_view, name="booking-cancel"),
    path("<int:pk>/request-review/", views.request_review_view, name="request-review"),
]
