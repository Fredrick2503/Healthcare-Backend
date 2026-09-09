from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

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
