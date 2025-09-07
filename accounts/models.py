# airbnb-clone-project/accounts/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Application user model using email for authentication.

    Includes simple role via `user_type` and a phone number field, suitable for Ghanaian context
    (e.g., MTN/Vodafone numbers).
    """

    # Remove username and use email instead
    username = None
    email = models.EmailField(unique=True)

    # User type (guest or host)
    USER_TYPE_CHOICES = (
        ("guest", "Guest"),
        ("host", "Host"),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default="guest",
        help_text="Designates whether the user is a guest or host.",
    )

    # Additional fields
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Ghanaian phone number (e.g., 0244123456)",
    )

    # Verification and activation
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this user has verified their email address.",
    )

    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
