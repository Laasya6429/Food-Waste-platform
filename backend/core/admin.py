from django.contrib import admin
from .models import User, Donation, FoodRequest, ImpactLog, FoodRiskAssessment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "role", "email")
    list_filter = ("role",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "food_type",
        "quantity_kg",
        "status",
        "expiry_time",
        "donor",
    )
    list_filter = ("status", "food_type")
    search_fields = ("donor__username",)

@admin.action(description="Approve selected food requests")
def approve_requests(modeladmin, request, queryset):
    queryset.update(status="APPROVED")

@admin.register(FoodRequest)
class FoodRequestAdmin(admin.ModelAdmin):
    list_display = ("donation", "ngo", "status", "pickup_time")
    actions = [approve_requests]


@admin.register(FoodRiskAssessment)
class FoodRiskAdmin(admin.ModelAdmin):
    list_display = ("donation", "risk_level", "assessed_at")


@admin.register(ImpactLog)
class ImpactAdmin(admin.ModelAdmin):
    list_display = (
        "donation",
        "meals_saved",
        "food_saved_kg",
        "co2_saved_kg",
    )


from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("rated_user", "rated_by", "rating", "created_at")
    list_filter = ("rating", "created_at")


