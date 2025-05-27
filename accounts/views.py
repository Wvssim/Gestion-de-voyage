from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm
from django.contrib.auth.models import User
def register(request):
    """Register a new user"""
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create the user but don't save yet
            new_user = user_form.save(commit=False)
            # Set the password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the user
            new_user.save()
            
            # Authenticate and login the user
            user = authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, 'Registration successful. Welcome!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Registration successful but unable to log in. Please log in.')
                return redirect('login')
    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': user_form})

@login_required
def profile(request):
    """View and update user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user's bookings
    bookings = request.user.bookings.all().order_by('-booking_date')[:5]
    
    context = {
        'form': form,
        'bookings': bookings,
    }
    return render(request, 'accounts/profile.html', context)
