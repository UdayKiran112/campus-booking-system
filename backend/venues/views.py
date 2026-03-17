from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Venue, VenueAvailability, VenueImage
from .serializers import (
    VenueSerializer, VenueCreateSerializer, 
    VenueSearchSerializer, VenueAvailabilitySerializer
)


class VenueListView(generics.ListAPIView):
    """List all venues with filtering"""
    serializer_class = VenueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Venue.objects.filter(is_active=True)
        
        # Apply filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        venue_type = self.request.query_params.get('venue_type')
        if venue_type:
            queryset = queryset.filter(venue_type=venue_type)
        
        ownership = self.request.query_params.get('ownership')
        if ownership:
            queryset = queryset.filter(ownership=ownership)
        
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        min_capacity = self.request.query_params.get('min_capacity')
        if min_capacity:
            queryset = queryset.filter(capacity__gte=int(min_capacity))
        
        max_capacity = self.request.query_params.get('max_capacity')
        if max_capacity:
            queryset = queryset.filter(capacity__lte=int(max_capacity))
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset


class VenueDetailView(generics.RetrieveAPIView):
    """Get details of a specific venue"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsAuthenticated]


class VenueCreateView(generics.CreateAPIView):
    """Create a new venue (authority only)"""
    serializer_class = VenueCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Only authorities can create venues
        if not self.request.user.is_authority:
            raise permissions.PermissionDenied("Only authorities can create venues")
        
        serializer.save()


class VenueUpdateView(generics.UpdateAPIView):
    """Update venue details (authority only)"""
    queryset = Venue.objects.all()
    serializer_class = VenueCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        venue = self.get_object()
        
        # Check if user has permission to update this venue
        if not venue.can_user_approve(self.request.user):
            raise permissions.PermissionDenied("You don't have permission to update this venue")
        
        serializer.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def venue_categories_view(request):
    """Get all venue categories"""
    categories = [
        {'value': choice[0], 'label': choice[1]}
        for choice in Venue.VenueCategory.choices
    ]
    return Response(categories)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def venue_types_view(request):
    """Get venue types, optionally filtered by category"""
    category = request.query_params.get('category')
    
    venue_types = []
    for choice in Venue.VenueType.choices:
        # Map venue types to categories
        type_category = None
        if choice[0] in ['INDOOR_AUDITORIUM', 'OUTDOOR_AUDITORIUM']:
            type_category = 'CULTURAL'
        elif choice[0] in ['INDOOR_SPORTS', 'OUTDOOR_SPORTS']:
            type_category = 'SPORTS'
        elif choice[0] in ['SEMINAR_HALL', 'CLASSROOM', 'LABORATORY']:
            type_category = 'ACADEMICS'
        elif choice[0] in ['GUEST_HOUSE', 'HOSTEL_GUEST_ROOM']:
            type_category = 'ACCOMMODATION'
        
        if not category or type_category == category:
            venue_types.append({
                'value': choice[0],
                'label': choice[1],
                'category': type_category
            })
    
    return Response(venue_types)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def venue_pricing_view(request, pk):
    """Get pricing details for a venue based on current user"""
    try:
        venue = Venue.objects.get(pk=pk)
    except Venue.DoesNotExist:
        return Response(
            {'error': 'Venue not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    pricing = venue.get_pricing_for_user(request.user)
    
    return Response({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'user_role': request.user.role,
        'pricing': pricing
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_venue_view(request, pk):
    """Block a venue for specific dates (authority only)"""
    try:
        venue = Venue.objects.get(pk=pk)
    except Venue.DoesNotExist:
        return Response(
            {'error': 'Venue not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permission
    if not venue.can_user_approve(request.user):
        raise permissions.PermissionDenied("You don't have permission to block this venue")
    
    serializer = VenueAvailabilitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    availability = VenueAvailability.objects.create(
        venue=venue,
        created_by=request.user,
        **serializer.validated_data
    )
    
    return Response({
        'message': 'Venue availability updated',
        'availability': VenueAvailabilitySerializer(availability).data
    }, status=status.HTTP_201_CREATED)
