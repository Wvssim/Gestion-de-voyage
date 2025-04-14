from django import forms
from .models import Booking, Travel
from django.core.validators import MinValueValidator
from django.utils import timezone

class TravelSearchForm(forms.Form):
    """Form for searching and filtering travels"""
    destination = forms.CharField(max_length=100, required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    max_price = forms.DecimalField(decimal_places=2, required=False, min_value=0)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date should be after start date.")
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    """Form for creating a booking"""
    class Meta:
        model = Booking
        fields = ['num_seats']
        widgets = {
            'num_seats': forms.NumberInput(attrs={'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        self.available_seats = kwargs.pop('available_seats', 1)
        super().__init__(*args, **kwargs)
        self.fields['num_seats'].validators.append(MinValueValidator(1))
        self.fields['num_seats'].widget.attrs['max'] = self.available_seats
        self.fields['num_seats'].help_text = f'Available seats: {self.available_seats}'
    
    def clean_num_seats(self):
        num_seats = self.cleaned_data.get('num_seats')
        if num_seats > self.available_seats:
            raise forms.ValidationError(f"Only {self.available_seats} seats available.")
        return num_seats

class TravelForm(forms.ModelForm):
    """Form for creating/editing travels"""
    class Meta:
        model = Travel
        fields = ['name', 'destination', 'description', 'start_date', 'end_date', 
                  'price', 'total_seats', 'available_seats', 'image_url']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        total_seats = cleaned_data.get('total_seats')
        available_seats = cleaned_data.get('available_seats')
        
        # Validate dates
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")
            
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        # Validate seats
        if total_seats and available_seats:
            if available_seats > total_seats:
                raise forms.ValidationError("Available seats cannot exceed total seats.")
        
        return cleaned_data
