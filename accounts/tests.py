from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserRegistrationTest(TestCase):
    def test_registration_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_user(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'password2': 'testpassword123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_password_mismatch(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'password2': 'wrongpassword',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)  # Form displayed again with errors
        self.assertContains(response, "Passwords don't match")
        
        # Check that user was not created
        self.assertFalse(User.objects.filter(username='testuser').exists())

class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
    
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_failure(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)  # Form displayed again with errors
        self.assertContains(response, "Please enter a correct username and password")

class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("profile")}')
    
    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
    
    def test_profile_update(self):
        self.client.login(username='testuser', password='testpassword123')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check if user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
