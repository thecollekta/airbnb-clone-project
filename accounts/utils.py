# airbnb-clone-project/accounts/utils.py

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, smart_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode


def send_email(subject, recipient_list, template_name, context):
    """Send an email using the specified template."""
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_verification_email(request, user):
    """
    Send an email with a verification link to the user's email address.
    """
    # Generate token
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    # Get the frontend verification URL from settings
    frontend_url = settings.FRONTEND_BASE_URL
    verification_path = settings.EMAIL_VERIFICATION_URL.format(uid=uidb64, token=token)

    # Construct the full verification URL
    verification_url = f"{frontend_url}/{verification_path}"

    # Email subject and message
    subject = "Verify your email address"

    # Load and render the email template
    html_message = render_to_string(
        "emails/email_verification.html",
        {
            "user": user,
            "verification_url": verification_url,
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


def send_password_reset_email(request, user):
    """Send a password reset link to the user."""
    token_generator = PasswordResetTokenGenerator()
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = token_generator.make_token(user)

    current_site = get_current_site(request).domain
    relative_link = reverse(
        "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
    )
    abs_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}{relative_link}"

    context = {
        "user": user,
        "reset_url": abs_url,
        "site_name": current_site,
    }

    send_email(
        subject="Password Reset Request",
        recipient_list=[user.email],
        template_name="emails/password_reset_email.html",
        context=context,
    )
