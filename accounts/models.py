from django.db import models
from django.contrib.auth.models import User

# We're using Django's built-in User model for authentication
# This file is here for future extensions if needed

class Profile(models.Model):
    """
    Extension of the User model to store additional user information
    Can be extended in the future if needed
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add custom fields here as needed
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # Add more fields as needed
    
    def __str__(self):
        return f"{self.user.username}'s profile"
