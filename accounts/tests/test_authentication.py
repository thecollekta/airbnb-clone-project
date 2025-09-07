import json
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test user registration API."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'TestPass123',
            'password2': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0244123456',
            'user_type': 'guest',
        }
    
    def test_valid_registration(self):
        """Test user registration with valid data."""
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertFalse(User.objects.get().is_verified)
        self.assertIn('tokens', response.data)
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('access', response.data['tokens'])
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email."""
        # Create a user first
        User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            phone_number='0244123456'
        )
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_password_mismatch(self):
        """Test registration with mismatched passwords."""
        payload = self.valid_payload.copy()
        payload['password2'] = 'DifferentPass123'
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserLoginTestCase(APITestCase):
    """Test user login API."""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('accounts:token_obtain_pair')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123',
            first_name='Test',
            last_name='User',
            phone_number='0244123456',
            is_verified=True
        )
    
    def test_valid_login(self):
        """Test login with valid credentials."""
        response = self.client.post(
            self.login_url,
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123',
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            self.login_url,
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'WrongPassword',
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
    
    def test_unverified_user_login(self):
        """Test login with unverified user."""
        self.user.is_verified = False
        self.user.save()
        
        response = self.client.post(
            self.login_url,
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123',
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)


class PasswordResetTestCase(APITestCase):
    """Test password reset functionality."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123',
            first_name='Test',
            last_name='User',
            phone_number='0244123456',
            is_verified=True
        )
        self.request_reset_url = reverse('accounts:password-reset-email')
        
        # Generate token for testing
        self.token_generator = PasswordResetTokenGenerator()
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = self.token_generator.make_token(self.user)
        
        self.reset_confirm_url = reverse(
            'accounts:password-reset-confirm',
            kwargs={'uidb64': self.uidb64, 'token': self.token}
        )
        self.reset_complete_url = reverse('accounts:password-reset-complete')
    
    def test_password_reset_request(self):
        """Test password reset request."""
        response = self.client.post(
            self.request_reset_url,
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_password_reset_confirm(self):
        """Test password reset token validation."""
        response = self.client.get(self.reset_confirm_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
    
    def test_password_reset_complete(self):
        """Test password reset completion."""
        response = self.client.post(
            self.reset_complete_url,
            data=json.dumps({
                'password': 'NewTestPass123',
                'password2': 'NewTestPass123',
                'token': self.token,
                'uidb64': self.uidb64,
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTestPass123'))


class UserProfileTestCase(APITestCase):
    """Test user profile endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123',
            first_name='Test',
            last_name='User',
            phone_number='0244123456',
            is_verified=True
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        self.profile_url = reverse('accounts:user-profile')
        self.change_password_url = reverse('accounts:change-password')
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_profile(self):
        """Test updating user profile."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '0544123456',
            'bio': 'Test bio',
        }
        
        response = self.client.patch(
            self.profile_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.phone_number, '0544123456')
        self.assertEqual(self.user.bio, 'Test bio')
    
    def test_change_password(self):
        """Test changing user password."""
        change_data = {
            'old_password': 'TestPass123',
            'new_password': 'NewTestPass123',
            'new_password2': 'NewTestPass123',
        }
        
        response = self.client.put(
            self.change_password_url,
            data=json.dumps(change_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTestPass123'))
    
    def test_change_password_invalid_old_password(self):
        """Test changing password with invalid old password."""
        change_data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewTestPass123',
            'new_password2': 'NewTestPass123',
        }
        
        response = self.client.put(
            self.change_password_url,
            data=json.dumps(change_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
