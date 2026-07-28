import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentications.api.serializers import (
    AuthenticationChangePasswordSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    SignUpSerializer,
    TokenRefreshSerializer,
    UserLoginSerializer,
)
from apps.authentications.services import AuthenticationService
from utils.response.resp import APIResponse

logger = logging.getLogger(__name__)


class LoginAPIView(APIView):
    """
    AllowAny is used because a user is not authenticated yet at login,
    this endpoint is the entry point to obtain a token.
    """

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

        email = login_serializer.validated_data["email"]

        try:
            user = AuthenticationService.authenticate_user(email)
        except ValueError as e:
            return Response(
                APIResponse.get_response(message=str(e)),
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    """
    AllowAny is used because the refresh token itself (from the HttpOnly cookie)
    is the credential here, not a session auth header.
    """

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
    """
    AllowAny is used because the user is not logged in when resetting
    a forgotten password, the reset token itself is the credential.
    """

    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        try:
            AuthenticationService.reset_password(token, new_password)
        except ValueError as e:
            return Response(
                APIResponse.get_response(
                    message=str(e),
                    error={"token": str(e)},
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        AuthenticationService.change_password(
            request.user, serializer.validated_data["new_password"]
        )

        return Response(
            APIResponse.get_response(message="Password changed successfully."),
            status=status.HTTP_200_OK,
        )


class SignUpAPIView(APIView):
    """
    AllowAny is used because a new user has no account or token yet,
    this endpoint is how an account gets created in the first place.
    """

    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=SignUpSerializer)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, access_token, refresh_token = AuthenticationService.register_user(
            serializer
        )

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