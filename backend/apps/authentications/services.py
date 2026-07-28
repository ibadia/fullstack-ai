from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from utils import utils


class AuthenticationService:
    @staticmethod
    def process_login(email: str):
        """Updates last_login and returns the user object. Raises ValueError if not found."""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("No user found with this email address.")
        
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return user

    @staticmethod
    def process_signup(serializer):
        """Saves user from serializer and generates tokens."""
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return user, str(refresh.access_token), str(refresh)

    @staticmethod
    def process_password_reset(token: str, new_password: str):
        """Validates token and updates user password."""
        data = utils.validate_token(token)
        if not data:
            raise ValueError("Invalid or expired token.")

        user_id = data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        user.set_password(new_password)
        user.pwd_reset_required = False
        user.save()

    @staticmethod
    def process_password_change(user: User, new_password: str):
        """Updates an authenticated user's password."""
        user.set_password(new_password)
        user.pwd_reset_required = False
        user.save()
