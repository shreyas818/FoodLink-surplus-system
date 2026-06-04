from django.db import models

class FoodDonation(models.Model):
    STATUS_CHOICES = [
        ('LISTED', 'Listed'),
        ('ASSIGNED', 'NGO Assigned'),
        ('PICKED_UP', 'Picked Up'),
        ('DELIVERED', 'Reached Destination'),
    ]
    
    food_type = models.CharField(max_length=255)  # e.g., "Surplus Vegetable Curry & Rice"
    quantity_kg = models.IntegerField()             # e.g., 25
    expiry_hours = models.CharField(max_length=50) # e.g., "Next 2 Hours"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LISTED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_type} - {self.quantity_kg}kg ({self.status})"
    
from django.contrib.auth.models import AbstractUser

#=====Model for user login=====
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('DONOR', 'Donor'),
        ('NGO', 'NGO'),
        ('VOLUNTEER', 'Volunteer'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='DONOR')

    def __str__(self):
        return f"{self.username} ({self.role})"

#=====Model for contact messages=====
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    partner_type = models.CharField(max_length=100)  # e.g., "Restaurant Partner", "NGO Partner", "Individual Volunteer"
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.partner_type} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"