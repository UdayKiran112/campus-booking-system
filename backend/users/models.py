from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    class UserRole(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        CLUB = 'CLUB', 'Club Representative'
        FACULTY = 'FACULTY', 'Faculty'
        DEPARTMENT_HEAD = 'DEPT_HEAD', 'Department Head'
        SCHOOL_OFFICE = 'SCHOOL_OFFICE', 'School Office'
        WARDEN = 'WARDEN', 'Warden'
        ADMIN = 'ADMIN', 'Administration'
        EXTERNAL = 'EXTERNAL', 'External Organization'
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT
    )
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_authority(self):
        """Check if user has authority approval rights"""
        return self.role in [
            self.UserRole.DEPARTMENT_HEAD,
            self.UserRole.SCHOOL_OFFICE,
            self.UserRole.WARDEN,
            self.UserRole.ADMIN
        ]
    
    @property
    def can_book_accommodation(self):
        """Check if user can book accommodation"""
        return self.role in [
            self.UserRole.FACULTY,
            self.UserRole.ADMIN,
            self.UserRole.EXTERNAL
        ]


class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    no_show_count = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    successful_bookings = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    @property
    def reliability_score(self):
        """Calculate user reliability based on booking history"""
        if self.total_bookings == 0:
            return 100
        return int((self.successful_bookings / self.total_bookings) * 100)
