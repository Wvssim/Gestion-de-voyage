import os
import sys
import random
import datetime
from decimal import Decimal

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_booking.settings')

import django
django.setup()

# Import models after django setup
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from accounts.models import Profile
from bookings.models import Travel, Booking

def create_superuser():
    """Create a superuser if not already exists"""
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin1234'
        )
        Profile.objects.create(
            user=admin,
            phone_number='+1234567890',
            address='123 Admin Street, Admin City'
        )
        print('Superuser created: admin/admin1234')
    else:
        print('Superuser already exists')


def create_regular_users(num_users=5):
    """Create regular users if not enough exist"""
    current_count = User.objects.filter(is_staff=False).count()
    if current_count < num_users:
        for i in range(current_count + 1, num_users + 1):
            # Create regular user
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='user1234',
                first_name=f'User {i}',
                last_name=f'Lastname {i}'
            )
            # Create profile
            Profile.objects.create(
                user=user,
                phone_number=f'+98765{i}{i}{i}{i}{i}',
                address=f'{i}{i}{i} User Street, User City'
            )
        print(f'Created {num_users - current_count} regular users (username: user1, user2, etc. / password: user1234)')
    else:
        print('Enough regular users already exist')


def create_travel_packages(num_travels=10):
    """Create travel packages if not enough exist"""
    current_count = Travel.objects.count()
    if current_count < num_travels:
        # Sample destinations
        destinations = [
            'Paris, France', 'Rome, Italy', 'Barcelona, Spain', 'Amsterdam, Netherlands',
            'Prague, Czech Republic', 'Vienna, Austria', 'London, UK', 'Berlin, Germany',
            'Athens, Greece', 'Lisbon, Portugal', 'Tokyo, Japan', 'New York, USA',
            'Dubai, UAE', 'Sydney, Australia', 'Cairo, Egypt', 'Rio de Janeiro, Brazil',
            'Cape Town, South Africa', 'Bangkok, Thailand'
        ]
        
        # Sample travel names
        travel_prefixes = ['Amazing', 'Wonderful', 'Spectacular', 'Breathtaking', 'Exciting', 'Unforgettable']
        travel_suffixes = ['Vacation', 'Adventure', 'Trip', 'Journey', 'Experience', 'Getaway']
        
        # Sample descriptions
        description_templates = [
            "Experience the beauty and culture of {0} with this exclusive package. Enjoy guided tours, luxurious accommodations, and unforgettable experiences.",
            "Discover {0} like never before! This package includes visits to famous landmarks, authentic local cuisine, and comfortable stays in central locations.",
            "Immerse yourself in the charm of {0}. This carefully curated package offers the perfect balance of guided activities and free time to explore.",
            "Escape to {0} with our special travel deal. Ideal for travelers seeking a mix of adventure, relaxation, and cultural experiences.",
            "This premium {0} package offers exclusive access to top attractions, high-end accommodations, and personalized service throughout your stay."
        ]
        
        # Sample image URLs
        image_urls = [
            "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800",
            "https://images.unsplash.com/photo-1530521954074-e64f6810b32d",
            "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1",
            "https://images.unsplash.com/photo-1501785888041-af3ef285b470",
            "https://images.unsplash.com/photo-1503220317375-aaad61436b1b",
            "https://images.unsplash.com/photo-1528543606781-2f6e6857f318",
            "https://images.unsplash.com/photo-1549144511-f099e773c147"
        ]
        
        # Create travel packages
        for i in range(current_count + 1, num_travels + 1):
            destination = random.choice(destinations)
            
            # Create random dates in the future
            today = datetime.date.today()
            start_offset = random.randint(30, 180)  # Between 1 month and 6 months from now
            duration = random.randint(5, 14)  # Duration between 5 and 14 days
            
            start_date = today + datetime.timedelta(days=start_offset)
            end_date = start_date + datetime.timedelta(days=duration)
            
            # Random price between $500 and $3000
            price = Decimal(random.randint(50000, 300000)) / Decimal(100)
            
            # Random number of total seats between 20 and 50
            total_seats = random.randint(20, 50)
            
            # Random number of available seats (ensure some are still available)
            available_seats = random.randint(max(1, total_seats // 5), total_seats)
            
            # Create a name for the travel package
            name = f"{random.choice(travel_prefixes)} {destination} {random.choice(travel_suffixes)}"
            
            # Create a description
            description = random.choice(description_templates).format(destination)
            
            # Create the travel package
            Travel.objects.create(
                name=name,
                destination=destination,
                description=description,
                start_date=start_date,
                end_date=end_date,
                price=price,
                total_seats=total_seats,
                available_seats=available_seats,
                image_url=random.choice(image_urls)
            )
        
        print(f'Created {num_travels - current_count} travel packages')
    else:
        print('Enough travel packages already exist')


def create_bookings(num_bookings=15):
    """Create sample bookings if not enough exist"""
    current_count = Booking.objects.count()
    if current_count < num_bookings:
        users = User.objects.filter(is_staff=False)
        travels = Travel.objects.all()
        
        # Ensure we have users and travels to create bookings
        if not users or not travels:
            print('Cannot create bookings: need users and travel packages first')
            return
        
        statuses = ['confirmed', 'pending', 'cancelled']
        
        # Create bookings
        for i in range(current_count + 1, num_bookings + 1):
            user = random.choice(users)
            travel = random.choice(travels)
            
            # Don't book if no seats available
            if travel.available_seats <= 0:
                continue
                
            # Random number of seats between 1 and 5, but not more than available
            num_seats = min(random.randint(1, 5), travel.available_seats)
            
            # Random status, with higher probability of 'confirmed'
            status_weights = [0.7, 0.2, 0.1]  # 70% confirmed, 20% pending, 10% cancelled
            status = random.choices(statuses, weights=status_weights, k=1)[0]
            
            # Create booking date in the past but after travel was created
            days_ago = random.randint(1, 30)
            booking_date = make_aware(datetime.datetime.now() - datetime.timedelta(days=days_ago))
            
            # Create booking
            Booking.objects.create(
                user=user,
                travel=travel,
                booking_date=booking_date,
                num_seats=num_seats,
                status=status
            )
            
            # Update available seats only if booking is confirmed or pending
            if status != 'cancelled':
                travel.available_seats -= num_seats
                travel.save()
        
        print(f'Created {num_bookings - current_count} sample bookings')
    else:
        print('Enough sample bookings already exist')


if __name__ == '__main__':
    print('Starting database population script...')
    
    # Create users first
    create_superuser()
    create_regular_users(5)
    
    # Then create travel packages
    create_travel_packages(10)
    
    # Finally create bookings
    create_bookings(15)
    
    print('Database population completed!')