from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Travel, Booking
from .forms import BookingForm, TravelForm, TravelSearchForm

@login_required
def dashboard(request):
    """User dashboard showing bookings overview"""
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status='confirmed',
        travel__start_date__gte=timezone.now().date()
    ).order_by('travel__start_date')[:5]
    
    recent_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booking_date')[:5]
    
    context = {
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'bookings/dashboard.html', context)

def travel_list(request):
    """Display list of all available travels with search/filter functionality"""
    travels = Travel.objects.filter(
        start_date__gte=timezone.now().date(),
        available_seats__gt=0
    )
    
    form = TravelSearchForm(request.GET)
    if form.is_valid():
        # Apply filters if form is valid
        if form.cleaned_data.get('destination'):
            travels = travels.filter(destination__icontains=form.cleaned_data['destination'])
        
        if form.cleaned_data.get('start_date'):
            travels = travels.filter(start_date__gte=form.cleaned_data['start_date'])
            
        if form.cleaned_data.get('end_date'):
            travels = travels.filter(end_date__lte=form.cleaned_data['end_date'])
            
        if form.cleaned_data.get('max_price'):
            travels = travels.filter(price__lte=form.cleaned_data['max_price'])
    
    context = {
        'travels': travels,
        'form': form,
    }
    return render(request, 'bookings/travel_list.html', context)

def travel_detail(request, travel_id):
    """Display detailed information about a specific travel"""
    travel = get_object_or_404(Travel, pk=travel_id)
    
    context = {
        'travel': travel,
    }
    return render(request, 'bookings/travel_detail.html', context)

@login_required
def booking_create(request, travel_id):
    """Create a new booking for a travel"""
    travel = get_object_or_404(Travel, pk=travel_id)
    
    # Check if travel is still available
    if travel.is_fully_booked() or travel.is_past():
        messages.error(request, "This travel is no longer available for booking.")
        return redirect('travel_detail', travel_id=travel.id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, available_seats=travel.available_seats)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.travel = travel
            
            # Validate seats availability once more
            if booking.num_seats > travel.available_seats:
                messages.error(request, f"Only {travel.available_seats} seats available.")
                return redirect('booking_create', travel_id=travel.id)
                
            booking.save()
            messages.success(request, "Your booking has been confirmed!")
            return redirect('dashboard')
    else:
        form = BookingForm(available_seats=travel.available_seats)
    
    context = {
        'form': form,
        'travel': travel,
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_history(request):
    """Show user's booking history"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/booking_history.html', context)

@login_required
def booking_cancel(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if request.method == 'POST':
        if booking.can_be_cancelled():
            if booking.cancel():
                messages.success(request, "Your booking has been cancelled successfully.")
            else:
                messages.error(request, "Unable to cancel the booking.")
        else:
            messages.error(request, "This booking cannot be cancelled.")
        
        return redirect('booking_history')
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_cancel.html', context)

# Admin views
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    today = timezone.now().date()
    
    # Basic statistics
    total_users = User.objects.count()
    total_travels = Travel.objects.count()
    total_bookings = Booking.objects.count()
    active_travels = Travel.objects.filter(start_date__gte=today).count()
    
    # Bookings by status
    booking_stats = Booking.objects.values('status').annotate(count=Count('id'))
    
    # Most popular destinations
    popular_destinations = Travel.objects.values('destination').annotate(
        count=Count('bookings')
    ).order_by('-count')[:5]
    
    # Revenue
    revenue = Booking.objects.filter(status='confirmed').aggregate(
        total=Sum(models.F('num_seats') * models.F('travel__price'))
    )['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_travels': total_travels,
        'total_bookings': total_bookings,
        'active_travels': active_travels,
        'booking_stats': booking_stats,
        'popular_destinations': popular_destinations,
        'revenue': revenue,
    }
    return render(request, 'bookings/admin_dashboard.html', context)

@staff_member_required
def admin_users(request):
    """Admin view for user management"""
    from django.contrib.auth.models import User
    
    users = User.objects.all().order_by('-date_joined')
    
    # Count bookings for each user
    users_with_stats = []
    for user in users:
        bookings_count = Booking.objects.filter(user=user).count()
        users_with_stats.append({
            'user': user,
            'bookings_count': bookings_count,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
        })
    
    context = {
        'users': users_with_stats,
    }
    return render(request, 'bookings/admin_users.html', context)

@staff_member_required
def admin_travels(request):
    """Admin view for travel management"""
    travels = Travel.objects.all().order_by('-start_date')
    
    if request.method == 'POST':
        form = TravelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Travel created successfully!")
            return redirect('admin_travels')
    else:
        form = TravelForm()
    
    context = {
        'travels': travels,
        'form': form,
    }
    return render(request, 'bookings/admin_travels.html', context)

@staff_member_required
def admin_travel_edit(request, travel_id):
    """Edit a travel"""
    travel = get_object_or_404(Travel, pk=travel_id)
    
    if request.method == 'POST':
        form = TravelForm(request.POST, instance=travel)
        if form.is_valid():
            form.save()
            messages.success(request, "Travel updated successfully!")
            return redirect('admin_travels')
    else:
        form = TravelForm(instance=travel)
    
    context = {
        'form': form,
        'travel': travel,
    }
    return render(request, 'bookings/admin_travel_edit.html', context)

@staff_member_required
def admin_travel_delete(request, travel_id):
    """Delete a travel"""
    travel = get_object_or_404(Travel, pk=travel_id)
    
    if request.method == 'POST':
        # Check if there are any confirmed bookings
        if Booking.objects.filter(travel=travel, status='confirmed').exists():
            messages.error(request, "Cannot delete travel with confirmed bookings.")
            return redirect('admin_travels')
        
        travel.delete()
        messages.success(request, "Travel deleted successfully!")
        return redirect('admin_travels')
    
    context = {
        'travel': travel,
    }
    return render(request, 'bookings/admin_travel_delete.html', context)

@staff_member_required
def admin_bookings(request):
    """Admin view for booking management"""
    bookings = Booking.objects.all().order_by('-booking_date')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/admin_bookings.html', context)
