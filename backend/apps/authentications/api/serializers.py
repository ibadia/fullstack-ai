from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer as SimpleJWTTokenRefreshSerializer,
)

from apps.users.models import User


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "is_staff",
        )


class LoginSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, value):
        """
        Ensure email exists and always use lowercase for lookups.
        """

        email = value.lower()

        try:
            User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

    def validate(self, attrs):
        """
        Force email to lowercase before passing to SimpleJWT validation,
        so authentication and any returned data consistently use lowercase.
        """
        if "email" in attrs and isinstance(attrs["email"], str):
            attrs["email"] = attrs["email"].lower()

        # Let SimpleJWT generate the token payload
        data = super().validate(attrs)

        # Also expose the normalized email in validated_data
        # so views/tests can access it reliably.
        data["email"] = attrs.get("email")

        return data


class TokenRefreshSerializer(SimpleJWTTokenRefreshSerializer):
    refresh = serializers.CharField(required=True)


class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }

    def validate(self, attrs):
        """
        Check that start is before finish.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"].lower(),
            password=validated_data["password"],
            name=validated_data["email"].lower(),
        )
        return user


class AuthenticationChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs