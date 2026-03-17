from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    LoginSerializer, ChangePasswordSerializer, UserProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    logout(request)
    return Response({
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current logged-in user details"""
    return Response(UserSerializer(request.user).data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """Update user profile"""
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({
        'message': 'Profile updated successfully',
        'user': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    
    # Check old password
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({
            'error': 'Old password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Set new password
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    })


class UserListView(generics.ListAPIView):
    """List all users (admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by role if provided
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by department if provided
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        return queryset
