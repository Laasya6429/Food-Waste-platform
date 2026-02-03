from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('DONOR', 'Donor'),
        ('NGO', 'NGO'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    phone = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Donation(models.Model):
    FOOD_TYPE_CHOICES = (
        ('COOKED', 'Cooked Food'),
        ('PACKAGED', 'Packaged Food'),
        ('RAW', 'Raw Ingredients'),
    )

    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('REQUESTED', 'Requested'),
        ('PICKED_UP', 'Picked Up'),
        ('EXPIRED', 'Expired'),
    )

    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donations'
    )

    food_type = models.CharField(
        max_length=20,
        choices=FOOD_TYPE_CHOICES
    )

    description = models.TextField()

    quantity_kg = models.FloatField()

    cooked_time = models.DateTimeField(
        blank=True,
        null=True
    )

    expiry_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation {self.id} - {self.food_type} - {self.status}"


class FoodRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("COMPLETED", "Completed"), 
    )


    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name='requests'
    )

    ngo = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='food_requests'
    )

    pickup_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} - {self.status}"


class FoodRiskAssessment(models.Model):
    RISK_LEVELS = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )

    donation = models.OneToOneField(
        Donation,
        on_delete=models.CASCADE,
        related_name='risk'
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVELS
    )

    reason = models.TextField()

    assessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation {self.donation.id} - {self.risk_level}"


class ImpactLog(models.Model):
    donation = models.ForeignKey(
        Donation,
        on_delete=models.SET_NULL,
        null=True
    )

    meals_saved = models.PositiveIntegerField()
    food_saved_kg = models.FloatField()
    co2_saved_kg = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Impact {self.id} - Meals: {self.meals_saved}"
