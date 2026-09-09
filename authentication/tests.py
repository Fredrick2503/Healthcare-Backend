from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class UserModelTests(TestCase):
    """
    Unit tests for the custom User model (matching ER diagram).
    """

    def test_create_user_successful(self):
        user = User.objects.create_user(
            email='alice@example.com',
            name='Alice Smith',
            password='SecurePassword123!'
        )
        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.name, 'Alice Smith')
        self.assertTrue(user.check_password('SecurePassword123!'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertIn('Alice Smith', str(user))

    def test_create_superuser_successful(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Administrator',
            password='AdminPassword123!'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_email_must_be_unique(self):
        User.objects.create_user(
            email='unique@example.com',
            name='User One',
            password='Password123!'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='unique@example.com',
                name='User Two',
                password='Password123!'
            )

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                name='No Email User',
                password='Password123!'
            )

class AuthenticationAPITests(APITestCase):
    """
    Unit tests for registration, login, and profile API endpoints.
    """

    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.profile_url = reverse('auth_profile')
        self.test_user = User.objects.create_user(
            email='existing@example.com',
            name='Existing User',
            password='ExistingPassword123!'
        )

    def test_register_user_success(self):
        payload = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertEqual(response.data['user']['name'], 'New User')
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_register_duplicate_email_fails(self):
        payload = {
            'name': 'Duplicate User',
            'email': 'existing@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_missing_fields_fails(self):
        payload = {'email': 'missing@example.com'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        payload = {
            'email': 'existing@example.com',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'existing@example.com')

    def test_login_invalid_password_fails(self):
        payload = {
            'email': 'existing@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_email_fails(self):
        payload = {
            'email': 'unknown@example.com',
            'password': 'AnyPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_authenticated_success(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.test_user.email)

    def test_profile_unauthenticated_fails(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
