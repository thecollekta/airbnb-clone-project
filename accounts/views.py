# airbnb-clone-project/accounts/views.py

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    ChangePasswordSerializer,
    PasswordTokenCheckSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from accounts.utils import send_password_reset_email, send_verification_email

logger = logging.getLogger(__name__)


User = get_user_model()


class UserRegistrationView(generics.GenericAPIView):
    """
    Register a new user and send email verification.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send verification email
            send_verification_email(request, user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            response_data = {
                "message": "User registered successfully. Please check your email to verify your account.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_type": user.user_type,
                    "is_verified": user.is_verified,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Verify user's email address using the token sent to their email.
    """

    permission_classes = [AllowAny]
    serializer_class = None

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            if not user.is_verified:
                user.is_verified = True
                user.save()
                # Send welcome email after verification
                send_welcome_email(user)
                return Response(
                    {"message": "Email successfully verified!"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Email is already verified."}, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid verification link"}, status=status.HTTP_400_BAD_REQUEST
        )


def send_welcome_email(user):
    """
    Send a welcome email to the user after successful verification.
    """
    subject = "Welcome to Airbnb Clone!"

    # Load and render the email template
    html_message = render_to_string(
        "emails/welcome_email.html",
        {
            "user": user,
            "site_name": "Airbnb Clone",
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message=strip_tags(html_message),  # Fallback text version
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )


class RequestPasswordResetEmail(generics.GenericAPIView):
    """
    Request password reset email.
    """

    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)

        # Always return success to prevent email enumeration
        return Response(
            {
                "message": "If an account exists with this email, you will receive a password reset link"
            },
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(APIView):
    """
    API endpoint to validate password reset token.
    """

    serializer_class = PasswordTokenCheckSerializer

    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "The reset link is invalid or has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Valid credentials",
                    "uidb64": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "The reset link is invalid or has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    """
    Set new password after token validation.
    """

    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.data.get("uidb64")))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(
                user, serializer.data.get("token")
            ):
                return Response(
                    {"error": "Token is not valid, please request a new one"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.data.get("password"))
            user.save()

            return Response(
                {"message": "Password reset successful"}, status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View and update user profile.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set new password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            # Update the user's session auth hash to prevent logout
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, self.object)

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(generics.DestroyAPIView):
    """
    An endpoint for deleting user account.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # In a real application, you might want to deactivate instead of delete
        # user.is_active = False
        # user.save()

        # Log the user out
        from django.contrib.auth import logout

        logout(request)

        # Delete the user
        user.delete()

        return Response(
            {"message": "Account successfully deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
