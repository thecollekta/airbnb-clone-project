# airbnb-clone-project/users/views.py


from django.contrib.auth import update_session_auth_hash
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import ChangePasswordSerializer, UserProfileSerializer


class MeViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    Endpoints to get/update the authenticated user's profile.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        """
        Return the current user's profile.
        """
        return self.request.user

    def get_object(self):
        """
        Return the user making the request.
        """
        return self.request.user

    @extend_schema(
        operation_id="retrieve_me",
        description="Retrieve the authenticated user's profile.",
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
            status.HTTP_404_NOT_FOUND: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get the current user's profile.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        operation_id="update_me",
        description="Update the authenticated user's profile.",
        request=UserProfileSerializer,
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_400_BAD_REQUEST: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    def update(self, request, *args, **kwargs):
        """
        Update the current user's profile.
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        operation_id="partial_update_me",
        description="Partially update the authenticated user's profile.",
        request=UserProfileSerializer,
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_400_BAD_REQUEST: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @extend_schema(
        operation_id="delete_me",
        description="Delete the authenticated user's account.",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

    @extend_schema(
        methods=["GET"],
        operation_id="get_me",
        description="Get current user's profile (alias for retrieve)",
        responses={
            status.HTTP_200_OK: UserProfileSerializer,
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
    )
    @action(detail=False, methods=["GET"])
    def me(self, request):
        """
        Alias for retrieve to get the current user's profile.
        This endpoint is available at /api/v1/users/me/me/ (due to DRF's router)
        """
        return self.retrieve(request)

    @extend_schema(
        operation_id="change_password",
        description="Change the authenticated user's password.",
        request=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Password updated successfully",
                    }
                },
            },
            status.HTTP_400_BAD_REQUEST: {
                "type": "object",
                "properties": {
                    "old_password": {"type": "array", "items": {"type": "string"}},
                    "new_password": {"type": "array", "items": {"type": "string"}},
                    "new_password2": {"type": "array", "items": {"type": "string"}},
                },
            },
            status.HTTP_401_UNAUTHORIZED: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        },
        methods=["POST"],
    )
    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        """
        Change the authenticated user's password.
        """
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # Check old password
            if not request.user.check_password(
                serializer.validated_data["old_password"]
            ):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set new password
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save()

            # Update session auth hash to prevent logout
            update_session_auth_hash(request, request.user)

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
