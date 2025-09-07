# airbnb-clone-project/users/serializers.py

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize limited user fields for profile endpoints."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login"]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password2 = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """
        Check that the old password is correct.
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your old password was entered incorrectly. Please enter it again."
            )
        return value

    def validate(self, attrs):
        """
        Validate that the two password fields match.
        """
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )

        # Validate the new password
        try:
            validate_password(attrs["new_password"], self.context["request"].user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs

    def update(self, instance, validated_data):
        """
        Update the user's password.
        """
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

    def create(self, validated_data):
        # Not used but required by the serializer
        pass
