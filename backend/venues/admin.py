from django.contrib import admin
from .models import Venue, VenueAvailability, VenueImage


class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "venue_type",
        "ownership",
        "capacity",
        "is_active",
    ]
    list_filter = ["category", "venue_type", "ownership", "is_active"]
    search_fields = ["name", "location", "department"]
    inlines = [VenueImageInline]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "category", "venue_type", "location", "description")},
        ),
        (
            "Ownership & Control",
            {"fields": ("ownership", "controlling_authority", "department")},
        ),
        ("Capacity & Facilities", {"fields": ("capacity", "facilities")}),
        ("Pricing", {"fields": ("base_price", "security_deposit")}),
        ("Availability", {"fields": ("is_active", "available_from", "available_to")}),
    )


@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["venue", "date", "is_available", "reason", "created_by"]
    list_filter = ["is_available", "date"]
    search_fields = ["venue__name", "reason"]
    date_hierarchy = "date"


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ["venue", "caption", "is_primary", "uploaded_at"]
    list_filter = ["is_primary", "uploaded_at"]
    search_fields = ["venue__name", "caption"]
