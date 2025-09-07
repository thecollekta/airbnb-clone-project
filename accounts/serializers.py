# airbnb-clone-project/serializers.py

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    force_str,
)
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[password_validation.validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password2",
            "user_type",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "phone_number": {"required": True},
            "user_type": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        # Remove password2 from the data
        validated_data.pop("password2", None)

        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""

    token = serializers.CharField(max_length=255)
    uidb64 = serializers.CharField(max_length=255)

    class Meta:
        fields = ["token", "uidb64"]

    def validate(self, attrs):
        try:
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    {"token": "Token is not valid or has expired"}
                )

            if user.is_active:
                raise serializers.ValidationError(
                    {"email": "Email is already verified"}
                )

            attrs["user"] = user
            return attrs

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"token": "Token is not valid or has expired"}
            )


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset email."""

    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email", "").lower()

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            attrs["user"] = user
            return attrs

        raise serializers.ValidationError(
            {"email": "User with this email does not exist"}
        )


class SetNewPasswordSerializer(serializers.Serializer):
    """
    Serializer for setting a new password after password reset.
    """

    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    password2 = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate that the two passwords match and meet requirements.
        """
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")

        # Use Django's built-in password validation
        try:
            from django.contrib.auth.password_validation import validate_password

            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        # This method is required but we don't need to create anything
        pass

    def update(self, instance, validated_data):
        # This method is required but we don't need to update anything
        pass


class PasswordTokenCheckSerializer(serializers.Serializer):
    """
    Serializer for password reset token validation.
    """

    class Meta:
        fields = []

    def validate(self, attrs):
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "is_verified",
            "date_joined",
            "last_login",
            "profile_picture",
            "bio",
            "date_of_birth",
            "gender",
        ]
        read_only_fields = ["id", "is_verified", "date_joined", "last_login"]
        extra_kwargs = {
            "profile_picture": {"required": False},
            "bio": {"required": False, "allow_blank": True},
            "date_of_birth": {"required": False},
            "gender": {"required": False},
        }

    def update(self, instance, validated_data):
        # Handle profile picture update
        profile_picture = validated_data.pop("profile_picture", None)
        if profile_picture:
            instance.profile_picture = profile_picture

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[password_validation.validate_password],
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your old password was entered incorrectly."
            )
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user
