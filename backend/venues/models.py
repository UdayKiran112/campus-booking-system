from django.db import models
from users.models import User


class Venue(models.Model):
    """Base venue model"""
    
    class VenueCategory(models.TextChoices):
        CULTURAL = 'CULTURAL', 'Cultural'
        SPORTS = 'SPORTS', 'Sports'
        ACADEMICS = 'ACADEMICS', 'Academics'
        ACCOMMODATION = 'ACCOMMODATION', 'Accommodation'
    
    class VenueType(models.TextChoices):
        # Cultural
        INDOOR_AUDITORIUM = 'INDOOR_AUDITORIUM', 'Indoor Auditorium'
        OUTDOOR_AUDITORIUM = 'OUTDOOR_AUDITORIUM', 'Outdoor Auditorium'
        
        # Sports
        INDOOR_SPORTS = 'INDOOR_SPORTS', 'Indoor Sports Facility'
        OUTDOOR_SPORTS = 'OUTDOOR_SPORTS', 'Outdoor Sports Facility'
        
        # Academics
        SEMINAR_HALL = 'SEMINAR_HALL', 'Seminar Hall'
        CLASSROOM = 'CLASSROOM', 'Classroom'
        LABORATORY = 'LABORATORY', 'Laboratory'
        
        # Accommodation
        GUEST_HOUSE = 'GUEST_HOUSE', 'Guest House'
        HOSTEL_GUEST_ROOM = 'HOSTEL_GUEST_ROOM', 'Hostel Guest Room'
    
    class OwnershipType(models.TextChoices):
        ADMINISTRATION = 'ADMINISTRATION', 'Administration Controlled'
        DEPARTMENT = 'DEPARTMENT', 'Department Controlled'
        SCHOOL_OFFICE = 'SCHOOL_OFFICE', 'School Office Controlled'
        WARDEN_OFFICE = 'WARDEN_OFFICE', 'Warden Office Controlled'
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=VenueCategory.choices)
    venue_type = models.CharField(max_length=30, choices=VenueType.choices)
    ownership = models.CharField(max_length=20, choices=OwnershipType.choices)
    
    # Authority information
    controlling_authority = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='controlled_venues'
    )
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Venue details
    capacity = models.IntegerField()
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    facilities = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Availability
    is_active = models.BooleanField(default=True)
    available_from = models.TimeField(default='08:00:00')
    available_to = models.TimeField(default='22:00:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'venues'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'venue_type']),
            models.Index(fields=['ownership']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def can_user_approve(self, user):
        """Check if user can approve bookings for this venue"""
        if user.role == User.UserRole.ADMIN and self.ownership == self.OwnershipType.ADMINISTRATION:
            return True
        
        if user.role == User.UserRole.DEPARTMENT_HEAD and self.ownership == self.OwnershipType.DEPARTMENT:
            return user.department == self.department
        
        if user.role == User.UserRole.SCHOOL_OFFICE and self.ownership == self.OwnershipType.SCHOOL_OFFICE:
            return user.department == self.department
        
        if user.role == User.UserRole.WARDEN and self.ownership == self.OwnershipType.WARDEN_OFFICE:
            return True
        
        return False
    
    def get_pricing_for_user(self, user):
        """Calculate pricing based on user type"""
        if user.role == User.UserRole.FACULTY:
            # Faculty academic sessions are free
            return {
                'base_price': 0,
                'security_deposit': 0,
                'payment_type': 'FREE'
            }
        
        if user.role in [User.UserRole.STUDENT, User.UserRole.CLUB]:
            # Students and clubs pay security deposit
            return {
                'base_price': 0,
                'security_deposit': float(self.security_deposit),
                'payment_type': 'DEPOSIT'
            }
        
        if user.role == User.UserRole.EXTERNAL:
            # External organizations pay commercial rate
            return {
                'base_price': float(self.base_price),
                'security_deposit': float(self.security_deposit),
                'payment_type': 'COMMERCIAL'
            }
        
        # Default: usage fee
        return {
            'base_price': float(self.base_price),
            'security_deposit': 0,
            'payment_type': 'USAGE_FEE'
        }


class VenueAvailability(models.Model):
    """Track special availability rules for venues"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='special_availability')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'venue_availability'
        unique_together = ['venue', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.venue.name} - {self.date} ({'Available' if self.is_available else 'Blocked'})"


class VenueImage(models.Model):
    """Store venue images"""
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='venue_images')
    image = models.ImageField(upload_to='venue_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'venue_images'
        ordering = ['-is_primary', '-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.venue.name}"
