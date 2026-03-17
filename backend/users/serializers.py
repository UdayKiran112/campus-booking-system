from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    reliability_score = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "profile_picture",
            "no_show_count",
            "total_bookings",
            "successful_bookings",
            "reliability_score",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    is_authority = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "department",
            "phone_number",
            "employee_id",
            "student_id",
            "organization_name",
            "verified",
            "is_authority",
            "profile",
            "created_at",
        ]
        read_only_fields = ["id", "verified", "created_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
            "department",
            "phone_number",
            "employee_id",
            "student_id",
            "organization_name",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")

        # Validate role-specific fields
        role = data.get("role")
        if role == User.UserRole.STUDENT and not data.get("student_id"):
            raise serializers.ValidationError("Student ID is required for students")

        if role == User.UserRole.FACULTY and not data.get("employee_id"):
            raise serializers.ValidationError("Employee ID is required for faculty")

        if role == User.UserRole.EXTERNAL and not data.get("organization_name"):
            raise serializers.ValidationError(
                "Organization name is required for external users"
            )

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)

        # Create user profile
        UserProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
        else:
            raise serializers.ValidationError("Must include username and password")

        data["user"] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("New passwords do not match")
        return data
