from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Travel(models.Model):
    name = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_seats = models.PositiveIntegerField(default=30)
    available_seats = models.PositiveIntegerField(default=30)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.name} to {self.destination} ({self.start_date} to {self.end_date})"
    
    def is_fully_booked(self):
        return self.available_seats <= 0
    
    def is_past(self):
        return self.start_date < timezone.now().date()

class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    num_seats = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    class Meta:
        ordering = ['-booking_date']
        
    def __str__(self):
        return f"Booking {self.id} - {self.user.username} for {self.travel.name}"
    
    def calculate_total_price(self):
        return self.travel.price * self.num_seats
    
    def can_be_cancelled(self):
        # Allow cancellation if the travel hasn't started yet
        return self.status != 'cancelled' and self.travel.start_date > timezone.now().date()
    
    def cancel(self):
        if self.can_be_cancelled():
            # Update booking status
            self.status = 'cancelled'
            self.save()
            
            # Return seats to the travel
            self.travel.available_seats += self.num_seats
            self.travel.save()
            return True
        return False
    
    def save(self, *args, **kwargs):
        # If this is a new booking (not cancelled), reduce available seats
        if not self.pk and self.status != 'cancelled':
            travel = self.travel
            travel.available_seats -= self.num_seats
            travel.save()
        super().save(*args, **kwargs)
