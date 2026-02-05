from django.contrib.auth import get_user_model
from .utils import calculate_distance
from django.utils import timezone
from .models import FoodRiskAssessment
from django.core.mail import send_mail
from django.conf import settings
from .models import ImpactLog

User = get_user_model()


def find_nearby_ngos(donation, max_distance_km=10):
    ngos = User.objects.filter(
        role='NGO',
        latitude__isnull=False,
        longitude__isnull=False
    )

    nearby_ngos = []

    for ngo in ngos:
        distance = calculate_distance(
            donation.donor.latitude,
            donation.donor.longitude,
            ngo.latitude,
            ngo.longitude
        )

        if distance <= max_distance_km:
            nearby_ngos.append({
                "ngo": ngo,
                "distance_km": distance
            })

    # Sort by nearest first
    nearby_ngos.sort(key=lambda x: x['distance_km'])

    return nearby_ngos 




def assess_food_risk(donation):
    now = timezone.now()

    risk_level = "LOW"
    reason = "Food is safe for consumption"

    if donation.food_type == "COOKED" and donation.cooked_time:
        hours_passed = (now - donation.cooked_time).total_seconds() / 3600

        if hours_passed > 8:
            risk_level = "HIGH"
            reason = "Cooked food older than 8 hours"
        elif hours_passed > 4:
            risk_level = "MEDIUM"
            reason = "Cooked food older than 4 hours"

    elif donation.expiry_time:
        hours_left = (donation.expiry_time - now).total_seconds() / 3600

        if hours_left <= 0:
            risk_level = "HIGH"
            reason = "Food is expired"
        elif hours_left <= 24:
            risk_level = "MEDIUM"
            reason = "Food nearing expiry"

    FoodRiskAssessment.objects.create(
        donation=donation,
        risk_level=risk_level,
        reason=reason
    )


def notify_ngos(nearby_ngos, donation):
    for ngo_data in nearby_ngos:
        ngo = ngo_data["ngo"]

        send_mail(
            subject="New Food Donation Available",
            message=(
                f"Food Type: {donation.food_type}\n"
                f"Quantity: {donation.quantity_kg} kg\n"
                f"Expiry: {donation.expiry_time}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ngo.email],
            fail_silently=True,
        )

def calculate_impact(donation):
    food_kg = donation.quantity_kg

    meals_saved = int(food_kg / 0.5)
    co2_saved = round(food_kg * 2.5, 2)

    ImpactLog.objects.create(
        donation=donation,
        meals_saved=meals_saved,
        food_saved_kg=food_kg,
        co2_saved_kg=co2_saved,
    )
