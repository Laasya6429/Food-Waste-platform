from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    DonationViewSet, 
    FoodRequestViewSet,
    ImpactStatsView,
    HeatmapDataView,
    RatingViewSet
)

router = DefaultRouter()
router.register("donations", DonationViewSet, basename="donation")
router.register("requests", FoodRequestViewSet, basename="request")
router.register("ratings", RatingViewSet, basename="rating")

urlpatterns = router.urls + [
    path("stats/impact/", ImpactStatsView.as_view(), name="impact-stats"),
    path("stats/heatmap/", HeatmapDataView.as_view(), name="heatmap-data"),
]
