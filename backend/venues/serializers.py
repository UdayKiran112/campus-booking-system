from rest_framework import serializers
from .models import Venue, VenueAvailability, VenueImage
from users.serializers import UserSerializer


class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = ['id', 'image', 'caption', 'is_primary', 'uploaded_at']


class VenueAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueAvailability
        fields = ['id', 'date', 'is_available', 'reason']


class VenueSerializer(serializers.ModelSerializer):
    controlling_authority_details = UserSerializer(source='controlling_authority', read_only=True)
    venue_images = VenueImageSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    venue_type_display = serializers.CharField(source='get_venue_type_display', read_only=True)
    ownership_display = serializers.CharField(source='get_ownership_display', read_only=True)
    
    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'category', 'category_display', 'venue_type', 
            'venue_type_display', 'ownership', 'ownership_display',
            'controlling_authority', 'controlling_authority_details',
            'department', 'capacity', 'location', 'description', 
            'facilities', 'base_price', 'security_deposit',
            'is_active', 'available_from', 'available_to',
            'venue_images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VenueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            'name', 'category', 'venue_type', 'ownership',
            'controlling_authority', 'department', 'capacity', 
            'location', 'description', 'facilities',
            'base_price', 'security_deposit',
            'available_from', 'available_to'
        ]
    
    def validate(self, data):
        # Validate ownership-specific requirements
        if data['ownership'] == Venue.OwnershipType.DEPARTMENT and not data.get('department'):
            raise serializers.ValidationError("Department is required for department-controlled venues")
        
        return data


class VenueSearchSerializer(serializers.Serializer):
    """Serializer for venue search parameters"""
    category = serializers.ChoiceField(
        choices=Venue.VenueCategory.choices,
        required=False
    )
    venue_type = serializers.ChoiceField(
        choices=Venue.VenueType.choices,
        required=False
    )
    ownership = serializers.ChoiceField(
        choices=Venue.OwnershipType.choices,
        required=False
    )
    min_capacity = serializers.IntegerField(required=False, min_value=1)
    max_capacity = serializers.IntegerField(required=False, min_value=1)
    department = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False)
