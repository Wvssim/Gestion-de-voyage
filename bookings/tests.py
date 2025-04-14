from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Travel, Booking
import datetime

class TravelModelTests(TestCase):
    def setUp(self):
        # Create a test travel
        self.travel = Travel.objects.create(
            name="Test Travel",
            destination="Test Destination",
            description="Test Description",
            start_date=timezone.now().date() + datetime.timedelta(days=10),
            end_date=timezone.now().date() + datetime.timedelta(days=20),
            price=100.00,
            total_seats=30,
            available_seats=30
        )
    
    def test_is_fully_booked(self):
        self.assertFalse(self.travel.is_fully_booked())
        self.travel.available_seats = 0
        self.travel.save()
        self.assertTrue(self.travel.is_fully_booked())
    
    def test_is_past(self):
        self.assertFalse(self.travel.is_past())
        self.travel.start_date = timezone.now().date() - datetime.timedelta(days=1)
        self.travel.save()
        self.assertTrue(self.travel.is_past())

class BookingModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a test travel
        self.travel = Travel.objects.create(
            name="Test Travel",
            destination="Test Destination",
            description="Test Description",
            start_date=timezone.now().date() + datetime.timedelta(days=10),
            end_date=timezone.now().date() + datetime.timedelta(days=20),
            price=100.00,
            total_seats=30,
            available_seats=30
        )
        
        # Create a test booking
        self.booking = Booking.objects.create(
            user=self.user,
            travel=self.travel,
            num_seats=2,
            status='confirmed'
        )
    
    def test_calculate_total_price(self):
        self.assertEqual(self.booking.calculate_total_price(), 200.00)
    
    def test_can_be_cancelled(self):
        self.assertTrue(self.booking.can_be_cancelled())
        
        # Test with past travel date
        past_travel = Travel.objects.create(
            name="Past Travel",
            destination="Past Destination",
            description="Past Description",
            start_date=timezone.now().date() - datetime.timedelta(days=1),
            end_date=timezone.now().date() + datetime.timedelta(days=5),
            price=100.00,
            total_seats=30,
            available_seats=30
        )
        
        past_booking = Booking.objects.create(
            user=self.user,
            travel=past_travel,
            num_seats=1,
            status='confirmed'
        )
        
        self.assertFalse(past_booking.can_be_cancelled())
    
    def test_cancel(self):
        initial_available_seats = self.travel.available_seats
        self.booking.cancel()
        
        # Refresh from database
        self.booking.refresh_from_db()
        self.travel.refresh_from_db()
        
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.travel.available_seats, initial_available_seats + self.booking.num_seats)

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        
        # Create test travels
        self.travel1 = Travel.objects.create(
            name="Test Travel 1",
            destination="Destination 1",
            description="Description 1",
            start_date=timezone.now().date() + datetime.timedelta(days=10),
            end_date=timezone.now().date() + datetime.timedelta(days=20),
            price=100.00,
            total_seats=30,
            available_seats=30
        )
        
        self.travel2 = Travel.objects.create(
            name="Test Travel 2",
            destination="Destination 2",
            description="Description 2",
            start_date=timezone.now().date() + datetime.timedelta(days=15),
            end_date=timezone.now().date() + datetime.timedelta(days=25),
            price=150.00,
            total_seats=20,
            available_seats=20
        )
    
    def test_travel_list_view(self):
        response = self.client.get(reverse('travel_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Travel 1")
        self.assertContains(response, "Test Travel 2")
    
    def test_travel_detail_view(self):
        response = self.client.get(reverse('travel_detail', args=[self.travel1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Travel 1")
        self.assertContains(response, "Destination 1")
    
    def test_dashboard_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("dashboard")}')
    
    def test_dashboard_view_logged_in(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_booking_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('booking_create', args=[self.travel1.id]))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        post_data = {
            'num_seats': 2
        }
        response = self.client.post(reverse('booking_create', args=[self.travel1.id]), post_data)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Check if booking was created
        self.assertTrue(Booking.objects.filter(user=self.user, travel=self.travel1).exists())
        
        # Check if available seats were updated
        self.travel1.refresh_from_db()
        self.assertEqual(self.travel1.available_seats, 28)
    
    def test_admin_views_redirect_if_not_staff(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_admin_views_accessible_if_staff(self):
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
