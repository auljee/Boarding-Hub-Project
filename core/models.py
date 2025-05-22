from django.db import models
from django.contrib.auth.models import User
from datetime import date

class HouseOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    boarding_house_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='owner_profiles/', null=True, blank=True)

    def __str__(self):
        return self.boarding_house_name

class Room(models.Model):
    owner = models.ForeignKey(HouseOwner, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20, null=True, blank=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"Room {self.room_number} - {self.owner.boarding_house_name}"



class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    tenant_image = models.ImageField(upload_to='tenant_profiles/', null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_contact = models.CharField(max_length=15, blank=True, null=True)
    guardian_address = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=10,
        choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')],
        default='unpaid'
    )
    rent_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        blank=True,  # Optional in forms
        null=True    # Optional in database
    )

    def __str__(self):
        return self.full_name

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    notes = models.TextField(blank=True, null=True)  # Add the 'notes' field here 
    def __str__(self):
        return f"{self.tenant.full_name} - {self.month}"
