import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentications.api.serializers import (
    AuthenticationChangePasswordSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    SignUpSerializer,
    TokenRefreshSerializer,
    UserLoginSerializer,
)
from apps.users.models import User
from utils import utils
from utils.response.resp import APIResponse

logger = logging.getLogger(__name__)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        req_data = request.data
        login_serializer = LoginSerializer(data=req_data)

        if not login_serializer.is_valid():
            return Response(
                APIResponse.get_response(
                    message="Validation error",
                    error=login_serializer.errors,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            email = login_serializer.validated_data["email"]
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                APIResponse.get_response(
                    message="No user found with this email address.",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update last login timestamp
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        user_serializer = UserLoginSerializer(user)
        access_token = login_serializer.validated_data.get("access")
        refresh_token = login_serializer.validated_data.get("refresh")
        
        data = {
            "user": user_serializer.data,
            "token": {"access": access_token},
        }
        
        response = Response(
            APIResponse.get_response(
                data=data,
            )
        )
        
        # Set refresh token in HttpOnly cookie
        if refresh_token:
            response.set_cookie(
                "refresh",
                refresh_token,
                httponly=True,
                samesite="Lax",
                # secure=True  # Ensure HTTPS in production
            )
            
        return response


class RefreshTokenAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response(
                APIResponse.get_response(
                    message="No refresh token provided.",
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
        # Passing it to serializer as 'refresh'
        req_data = request.data.copy()
        req_data["refresh"] = refresh_token
        
        serializer = TokenRefreshSerializer(data=req_data)
        serializer.is_valid(raise_exception=True)
        data = {
            "token": {"access": serializer.validated_data.get("access")},
        }
        return Response(
            APIResponse.get_response(
                data=data,
            )
        )


class ResetPasswordAPI(APIView):
    permission_classes = (AllowAny,)
    """
    Handles password reset using a token.
    """

    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request):
        # Validate new password
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        # Validate token and retrieve user ID
        data = utils.validate_token(token)
        if not data:
            # TODO: generic exception raise
            return Response(
                APIResponse.get_response(
                    message="Invalid or expired token.",
                    error={"token": "Invalid or expired token."},
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        # Set new password and clear password reset requirement
        user.set_password(serializer.validated_data["password"])
        user.pwd_reset_required = False
        user.save()

        return Response(
            APIResponse.get_response(
                message="Password has been reset successfully.",
            ),
            status=status.HTTP_200_OK,
        )


class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=AuthenticationChangePasswordSerializer)
    def post(self, request):
        serializer = AuthenticationChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.pwd_reset_required = False
        user.save()
        return Response(
            APIResponse.get_response(message="Password changed successfully."),
            status=status.HTTP_200_OK,
        )


class SignUpAPIView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=SignUpSerializer)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        tokens = {
            "access": access_token,
        }

        user_serializer = UserLoginSerializer(user)
        data = {
            "user": user_serializer.data,
            "token": tokens,
        }
        
        response = Response(
            APIResponse.get_response(message="User created successfully.", data=data),
            status=status.HTTP_201_CREATED,
        )
        
        response.set_cookie(
            "refresh",
            refresh_token,
            httponly=True,
            samesite="Lax",
        )
        return response
